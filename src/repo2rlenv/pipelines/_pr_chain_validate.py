"""Validate a chain's stages inside the bootstrap container.

Computes each stage's FAIL_TO_PASS and PASS_TO_PASS sets, which is what makes
the milestone gradeable at all. The protocol is simpler than `pr_runtime`'s
because a chain replays real history: there is no patch to apply and therefore
no patch that can fail to apply.

Per stage, inside one container:

  1. `git reset --hard <carry_commit>`  → the tree the agent starts from
     → run the stage's targeted tests → pre-status
  2. `git reset --hard <after_commit>`  → the gold tree
     → run the same tests           → post-status
  3. FAIL_TO_PASS = failing or absent in (1) and passing in (2)
     PASS_TO_PASS = passing in both

A stage with an empty FAIL_TO_PASS set has no oracle — its change did not move
any test — so it cannot be graded and the chain is rejected or trimmed. That
check is what stops a chain from silently containing unreachable milestones.

The same stage tests must also pass at the chain head. This keeps the
whole-chain oracle valid after later history changes those tests or their
dependencies.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass, field, replace
from enum import StrEnum
from pathlib import Path

from repo2rlenv.bootstrap.docker import DockerSandbox
from repo2rlenv.log_parsers import parse_logs
from repo2rlenv.pipelines._pr_chain_graph import Chain, ChainStage, chain_fetch_depth
from repo2rlenv.pipelines.pr_runtime import (
    normalize_test_cmds_for_runtime,
    targeted_test_cmds_for_pr,
)
from repo2rlenv.pipelines.pr_runtime_validate import (
    _ensure_git,
    _slice_test_output,
)

logger = logging.getLogger(__name__)

PASSED = "PASSED"

# Bump when the validation algorithm changes; cached verdicts from an older
# algorithm must never be reused.
CACHE_SCHEMA_VERSION = 2


class StageStatus(StrEnum):
    """Per-stage oracle outcome. Values are telemetry keys — do not rename."""

    VERIFIED = "verified"
    NO_ORACLE = "no_oracle"
    UNPARSEABLE = "unparseable"
    NO_REGRESSION_GUARD = "no_regression_guard"


class ChainStatus(StrEnum):
    """Whole-chain outcome. Values are telemetry keys — do not rename."""

    VERIFIED = "verified"
    TOO_FEW_STAGES = "too_few_stages"
    FETCH_FAILED = "fetch_failed"


_GIT_CLEAN = (
    "git clean -fdx -e .venv -e venv -e __pycache__ -e .tox "
    "-e node_modules -e target -e vendor -e .gradle -e .next -e .pytest_cache || true"
)


@dataclass(slots=True)
class StageValidation:
    """Per-stage oracle, or the reason the stage has none."""

    index: int
    status: StageStatus
    test_cmds: list[str] = field(default_factory=list)
    fail_to_pass: list[str] = field(default_factory=list)
    pass_to_pass: list[str] = field(default_factory=list)
    reason: str = ""

    @property
    def verified(self) -> bool:
        return self.status == StageStatus.VERIFIED


@dataclass(slots=True)
class ChainValidation:
    """Outcome of validating a whole chain."""

    status: ChainStatus
    stages: list[StageValidation] = field(default_factory=list)
    reason: str = ""

    @property
    def verified_stages(self) -> list[StageValidation]:
        return [s for s in self.stages if s.verified]


class StageValidationCache:
    """Durable per-stage oracle cache, shared across processes.

    Validating one stage costs four test runs, and a 100-step chain needs
    ~120 of them, so revalidation after an interrupted batch used to start
    from zero. With the cache, the expensive part is idempotent across
    restarts — and across workers: run N workers over the *same* selection
    and each stage is validated once globally, whichever worker reaches it
    first. Emission is deterministic and the output-dir check makes duplicate
    task writes harmless, so this is stage-level parallelism with no merge
    step and no coordination.
    """

    def __init__(self, path: Path) -> None:
        # busy_timeout: multiple workers share the file; a writer blocks
        # briefly rather than erroring.
        self._db = sqlite3.connect(str(path), timeout=30)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS stage_validation ("
            " key TEXT PRIMARY KEY,"
            " status TEXT NOT NULL,"
            " test_cmds TEXT NOT NULL,"
            " fail_to_pass TEXT NOT NULL,"
            " pass_to_pass TEXT NOT NULL,"
            " reason TEXT NOT NULL)"
        )
        self._db.commit()

    def key(
        self,
        chain: Chain,
        stage: ChainStage,
        base_test_cmds: list[str],
        language: str | None,
        *,
        max_pass_to_pass: int,
        min_pass_to_pass: int,
    ) -> str:
        """Content key for one stage's verdict: every input that can change it."""
        payload = {
            "v": CACHE_SCHEMA_VERSION,
            "base": chain.base_commit,
            "before": stage.before_commit,
            "carry": stage.carry_commit,
            "after": stage.after_commit,
            "test_paths": sorted(stage.test_paths),
            "test_cmds": stage_test_cmds(stage, base_test_cmds),
            "language": language,
            "max_p2p": max_pass_to_pass,
            "min_p2p": min_pass_to_pass,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def get(self, key: str) -> StageValidation | None:
        row = self._db.execute(
            "SELECT status, test_cmds, fail_to_pass, pass_to_pass, reason"
            " FROM stage_validation WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        status, test_cmds, f2p, p2p, reason = row
        return StageValidation(
            index=0,  # rewritten by the caller; indices are per-chain
            status=StageStatus(status),
            test_cmds=json.loads(test_cmds),
            fail_to_pass=json.loads(f2p),
            pass_to_pass=json.loads(p2p),
            reason=reason,
        )

    def put(self, key: str, stage: StageValidation) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO stage_validation"
            " (key, status, test_cmds, fail_to_pass, pass_to_pass, reason)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                key,
                str(stage.status),
                json.dumps(stage.test_cmds),
                json.dumps(stage.fail_to_pass),
                json.dumps(stage.pass_to_pass),
                stage.reason,
            ),
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()


def _stage_script(
    commit: str,
    test_cmds: list[str],
    *,
    tests_from: str,
    test_paths: tuple[str, ...],
) -> str:
    """Reset to a real commit, install a chosen version of the tests, and run them.

    `tests_from` decides which revision of the test files grades this run, and the
    choice is not cosmetic — the environment itself uses two different versions.
    Mid-run, the stage's Harbor step grades with the tests as they stood at
    that stage. The chain-head runs check the whole-chain oracle stays valid. A tree must therefore be checked with whichever version will
    actually be applied to it, or the oracle describes a situation that never
    occurs: grading every tree with the head's tests rejected stages whose final
    test file exercises behaviour a later stage introduces, and grading every tree
    with stage-era tests let a do-nothing agent collect 0.11.

    A test file absent at `tests_from` was deleted by then, so it is removed here
    too rather than left behind to be graded.
    """
    restore = [
        f"git checkout {tests_from} -- {path!r} 2>/dev/null || rm -f {path!r}"
        for path in test_paths
    ]
    return "\n".join(
        [
            "set -uxo pipefail",
            "cd /workspace",
            "git config --global --add safe.directory /workspace",
            f"git reset --hard {commit}",
            _GIT_CLEAN,
            *restore,
            # Markers go to STDOUT via echo: with `set -x`, a `:` no-op is traced
            # to STDERR while the runner writes STDOUT, and slicing between
            # stderr-only markers captures zero test lines.
            "echo R2E_START_TEST_OUTPUT",
            " && ".join(test_cmds) if test_cmds else "echo 'no test_cmds'",
            "echo R2E_END_TEST_OUTPUT",
        ]
    )


def fetch_chain_range(
    sandbox: DockerSandbox,
    chain: Chain,
    *,
    timeout: int = 900,
) -> tuple[bool, str]:
    """Make every commit the chain replays reachable in the container.

    The bootstrap image ships a depth-1 clone, so none of the chain's history is
    present. Fetching the head commit with a depth that covers the chain's span
    pulls the whole range in one request; a full unshallow would move hundreds of
    megabytes for history the chain never touches.

    One sandbox validates many chains in a batch, so this has to stay correct on
    a clone that earlier chains already deepened. Whether a fetch command
    *succeeded* is not the question — `git fetch --unshallow` exits non-zero on an
    already-complete repository — so success is decided only by whether the
    commits are present at the end.
    """
    if not _ensure_git(sandbox):
        return False, "git unavailable in sandbox"

    def missing_commits() -> list[str]:
        return [
            commit
            for commit in (chain.base_commit, chain.head_commit)
            if not sandbox.exec(
                f"git -C /workspace cat-file -e {commit} 2>/dev/null && echo OK", timeout=15
            ).stdout.count("OK")
        ]

    if not missing_commits():
        return True, ""  # an earlier chain in this sandbox already brought them in

    depth = chain_fetch_depth(chain)
    sandbox.exec(
        f"cd /workspace && git fetch --depth {depth} origin {chain.head_commit}",
        timeout=timeout,
    )
    missing = missing_commits()
    if missing:
        logger.warning(
            "chain %s still missing %s after a depth-%d fetch; deepening",
            chain.head_commit[:12],
            [c[:12] for c in missing],
            depth,
        )
        sandbox.exec(
            "cd /workspace && "
            "{ git rev-parse --is-shallow-repository | grep -qx true "
            "&& git fetch --unshallow origin; } "
            f"|| git fetch origin {chain.head_commit} "
            "|| git fetch --depth 5000 origin",
            timeout=timeout * 2,
        )
        missing = missing_commits()
    if missing:
        return False, f"commits absent after fetch: {[c[:12] for c in missing]}"
    return True, ""


def stage_test_cmds(stage: ChainStage, base_test_cmds: list[str]) -> list[str]:
    """Narrow the repo's test command to the stage's own test files.

    A monorepo suite takes tens of minutes; the stage's own test files take
    seconds, and they are the only tests its oracle can reference.
    """
    normalized = normalize_test_cmds_for_runtime(base_test_cmds)
    return targeted_test_cmds_for_pr(normalized, list(stage.test_paths))


def _statuses(
    sandbox: DockerSandbox,
    commit: str,
    test_cmds: list[str],
    *,
    tests_from: str,
    test_paths: tuple[str, ...],
    language: str | None,
    timeout: int,
) -> dict[str, str]:
    result = sandbox.exec(
        _stage_script(commit, test_cmds, tests_from=tests_from, test_paths=test_paths),
        timeout=timeout,
    )
    if result.timed_out:
        # A timed-out pytest run can still contain several parsed results. They
        # are incomplete, so using them would spend three more timeouts on a
        # stage whose oracle can never be trusted.
        logger.warning(
            "stage tests at %s timed out after %ds; rejecting partial results",
            commit[:12],
            timeout,
        )
        return {}
    log = result.truncated(max_chars=5_000_000)
    parsed = parse_logs(test_cmds, _slice_test_output(log), language=language)
    # parse_logs is typed over Literal statuses; the mapping is str-valued.
    return {name: str(status) for name, status in parsed.items()}


@dataclass(frozen=True, slots=True)
class _StageTrees:
    """A stage's per-test results on each tree the reward depends on.

    Naming them makes the oracle conditions readable: a fail-to-pass test is one
    that is broken where the agent starts and fixed where the agent finishes.
    """

    base: dict[str, str]
    start: dict[str, str]
    gold: dict[str, str]
    head: dict[str, str]

    def _passed(self, tree: dict[str, str], name: str) -> bool:
        return tree.get(name) == PASSED

    def is_fail_to_pass(self, name: str) -> bool:
        return (
            self._passed(self.gold, name)
            and self._passed(self.head, name)
            and not self._passed(self.start, name)
            and not self._passed(self.base, name)
        )

    def is_pass_to_pass(self, name: str) -> bool:
        return all(
            self._passed(tree, name) for tree in (self.base, self.start, self.gold, self.head)
        )


def _stage_tree_statuses(
    sandbox: DockerSandbox,
    chain: Chain,
    stage: ChainStage,
    cmds: list[str],
    *,
    language: str | None,
    timeout: int,
) -> _StageTrees | None:
    """Run a stage's tests on all four trees. None when the gold tree is unparseable.

    Each tree uses the test version that matches its role:

    * `start` and `gold` use the stage-era tests that the native Harbor step
      verifier restores.
    * `base` and `head` use the head tests to check that the whole-chain oracle
      starts at zero and ends at one.

    The gold tree runs first: if its output cannot be parsed there is no oracle to
    derive and the remaining runs would be wasted.
    """

    def at(commit: str, *, tests_from: str) -> dict[str, str]:
        return _statuses(
            sandbox,
            commit,
            cmds,
            tests_from=tests_from,
            test_paths=stage.test_paths,
            language=language,
            timeout=timeout,
        )

    gold = at(stage.after_commit, tests_from=stage.after_commit)
    if not gold:
        return None
    return _StageTrees(
        base=at(chain.base_commit, tests_from=chain.head_commit),
        start=at(stage.carry_commit, tests_from=stage.after_commit),
        gold=gold,
        head=at(chain.head_commit, tests_from=chain.head_commit),
    )


def _validate_stage(
    sandbox: DockerSandbox,
    chain: Chain,
    stage: ChainStage,
    base_test_cmds: list[str],
    *,
    language: str | None,
    max_pass_to_pass: int,
    min_pass_to_pass: int,
    timeout: int,
) -> StageValidation:
    """One stage's oracle from the four trees. Assumes `stage.test_paths` is set."""
    cmds = stage_test_cmds(stage, base_test_cmds)
    trees = _stage_tree_statuses(
        sandbox,
        chain,
        stage,
        cmds,
        language=language,
        timeout=timeout,
    )
    if trees is None:
        return StageValidation(
            index=stage.index,
            status=StageStatus.UNPARSEABLE,
            test_cmds=cmds,
            reason="no per-test results parsed from the gold tree",
        )

    fail_to_pass = sorted(name for name in trees.gold if trees.is_fail_to_pass(name))
    pass_to_pass = sorted(name for name in trees.gold if trees.is_pass_to_pass(name))
    if not fail_to_pass:
        return StageValidation(
            index=stage.index,
            status=StageStatus.NO_ORACLE,
            test_cmds=cmds,
            pass_to_pass=pass_to_pass[:max_pass_to_pass],
            reason="no test fails at the start and passes at the head",
        )
    if len(pass_to_pass) < min_pass_to_pass:
        return StageValidation(
            index=stage.index,
            status=StageStatus.NO_REGRESSION_GUARD,
            test_cmds=cmds,
            fail_to_pass=fail_to_pass,
            reason=(
                f"{len(pass_to_pass)} pass-to-pass test(s), need {min_pass_to_pass}: "
                "nothing would catch this stage breaking existing behaviour"
            ),
        )

    return StageValidation(
        index=stage.index,
        status=StageStatus.VERIFIED,
        test_cmds=cmds,
        fail_to_pass=fail_to_pass,
        pass_to_pass=pass_to_pass[:max_pass_to_pass],
    )


def validate_chain(
    *,
    sandbox: DockerSandbox,
    chain: Chain,
    base_test_cmds: list[str],
    language: str | None = None,
    min_stages: int = 8,
    max_pass_to_pass: int = 50,
    min_pass_to_pass: int = 1,
    timeout: int = 900,
    cache: StageValidationCache | None = None,
) -> ChainValidation:
    """Derive every stage's oracle against all four trees the reward depends on.

    A test earns a place in a stage's FAIL_TO_PASS set only if it:

    1. **fails at the chain base** — otherwise an agent that does nothing collects
       credit for it, which was measured at 0.11 mean reward before this check
       existed;
    2. **fails at the stage's own start** — otherwise the milestone is already
       satisfied when it opens and asks for no work;
    3. **passes at the stage's gold tree** — otherwise the stage's own change is
       not what makes it pass, and its Harbor step cannot award credit;
    4. **passes at the chain head** — otherwise the whole-chain oracle does not
       preserve that behavior.

    PASS_TO_PASS must pass on all four trees. Each tree uses the test version
    described by `_stage_tree_statuses`.

    Returns `status="verified"` when at least `min_stages` stages have a usable
    oracle. Stages without one are reported individually so the caller can trim
    the chain rather than discard it.
    """
    ok, reason = fetch_chain_range(sandbox, chain, timeout=timeout)
    if not ok:
        return ChainValidation(status=ChainStatus.FETCH_FAILED, reason=reason)

    stages: list[StageValidation] = []
    for stage in chain.stages:
        if not stage.test_paths:
            # Without a path to target, the repo's bare test command would run the
            # whole suite — minutes of work that can produce no per-stage oracle.
            stages.append(
                StageValidation(
                    index=stage.index,
                    status=StageStatus.NO_ORACLE,
                    reason="no test file of this stage exists at both its gold tree and the head",
                )
            )
            continue
        cache_key = None
        if cache is not None:
            cache_key = cache.key(
                chain,
                stage,
                base_test_cmds,
                language,
                max_pass_to_pass=max_pass_to_pass,
                min_pass_to_pass=min_pass_to_pass,
            )
            cached = cache.get(cache_key)
            if cached is not None:
                # Indices are per-chain; the cached verdict belongs to whatever
                # chain first validated this stage.
                stages.append(replace(cached, index=stage.index))
                continue
        stage_validation = _validate_stage(
            sandbox,
            chain,
            stage,
            base_test_cmds,
            language=language,
            max_pass_to_pass=max_pass_to_pass,
            min_pass_to_pass=min_pass_to_pass,
            timeout=timeout,
        )
        if cache is not None and cache_key is not None:
            cache.put(cache_key, stage_validation)
        stages.append(stage_validation)

    usable = [s for s in stages if s.verified]
    if len(usable) < min_stages:
        return ChainValidation(
            status=ChainStatus.TOO_FEW_STAGES,
            stages=stages,
            reason=f"{len(usable)} stage(s) have an oracle, need {min_stages}",
        )
    return ChainValidation(status=ChainStatus.VERIFIED, stages=stages)
