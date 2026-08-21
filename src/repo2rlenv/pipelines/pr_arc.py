"""pr_arc — standalone Terminal-Bench-style tasks derived from real PRs.

PRs are used as *ideas*, not as tasks: each emitted task is a self-contained
objective (a single hard stage, or a small arc of consecutive same-subsystem
stages composed into one change) with its own base tree, one binary
verification, and a reference solution. No chains, no per-step loop — one
Harbor task, one gradeable outcome.

Selection is evidence-based where measurement exists: stages a frontier model
failed during chain calibration are the known-hard pool, extended by size
heuristics (multi-file, multi-test changes) for the rest.

Difficulty note (TB3): a task that has many steps is not immediately hard, so
arcs stay small (2-5 stages) and compose one feature, not a queue of chores.
"""

from __future__ import annotations

import hashlib
import json
import re
import string
from dataclasses import dataclass, field
from importlib.resources import files as _resource_files
from pathlib import Path

from repo2rlenv.emitter.harbor import HarborTask
from repo2rlenv.git_local import binary_changed_files, file_at_commit, range_diff
from repo2rlenv.pipelines._env_guard import egress_guard_compose, git_history_scrub

# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------

MAX_ARC_STAGES = 5


@dataclass(frozen=True, slots=True)
class ArcStage:
    """One validated stage from a chain plan, with its measured difficulty."""

    index: int
    pr_number: int | None
    title: str
    instruction: str
    before_commit: str
    after_commit: str
    test_paths: list[str] = field(default_factory=list)
    fail_to_pass: list[str] = field(default_factory=list)
    pass_to_pass: list[str] = field(default_factory=list)
    source_paths: list[str] = field(default_factory=list)
    measured_reward: float | None = None  # from a calibration run, if present


@dataclass(frozen=True, slots=True)
class Arc:
    """A task candidate: one stage, or a small consecutive run as one change."""

    stages: tuple[ArcStage, ...]
    subsystem: str

    @property
    def base_commit(self) -> str:
        return self.stages[0].before_commit

    @property
    def final_commit(self) -> str:
        return self.stages[-1].after_commit

    @property
    def fail_to_pass(self) -> list[str]:
        out: list[str] = []
        for stage in self.stages:
            out.extend(stage.fail_to_pass)
        return out

    @property
    def pass_to_pass(self) -> list[str]:
        out: list[str] = []
        for stage in self.stages:
            out.extend(stage.pass_to_pass)
        return out

    @property
    def test_paths(self) -> list[str]:
        seen: dict[str, None] = {}
        for stage in self.stages:
            for path in stage.test_paths:
                seen.setdefault(path)
        return list(seen)


def load_arc_stages(plan_path: Path, measured: dict[int, float] | None = None) -> list[ArcStage]:
    """Read a chain task's plan.json into ArcStage records."""
    plan = json.loads(plan_path.read_text())
    stages = []
    for entry in plan["stages"]:
        stages.append(
            ArcStage(
                index=int(entry["index"]),
                pr_number=entry.get("pr_number"),
                title=str(entry["title"]),
                instruction=str(entry["instruction"]),
                before_commit=str(entry["before_commit"]),
                after_commit=str(entry["after_commit"]),
                test_paths=list(entry["test_paths"]),
                fail_to_pass=list(entry["fail_to_pass"]),
                pass_to_pass=list(entry["pass_to_pass"]),
                source_paths=list(entry.get("source_paths", [])),
                measured_reward=(measured or {}).get(int(entry["index"])),
            )
        )
    return stages


def select_arcs(stages: list[ArcStage]) -> list[Arc]:
    """Tile a chain's stages into consecutive arcs of at most MAX_ARC_STAGES.

    One arc is one feature-sized change: small enough that an expert who knows
    the answer lands it in a few hours, big enough to be one coherent objective
    rather than a queue of chores.
    """
    arcs: list[Arc] = []
    for start in range(0, len(stages), MAX_ARC_STAGES):
        group = tuple(stages[start : start + MAX_ARC_STAGES])
        if group:
            arcs.append(Arc(stages=group, subsystem="(arc)"))
    return arcs


def select_singletons(
    stages: list[ArcStage],
    *,
    hard_indices: set[int] | None = None,
    min_source_files: int = 3,
    min_f2p: int = 4,
) -> list[Arc]:
    """Standalone tasks for stages that are difficult on their own evidence."""
    hard = hard_indices or set()
    out: list[Arc] = []
    for stage in stages:
        measured_hard = stage.index in hard
        large = len(stage.source_paths) >= min_source_files or len(stage.fail_to_pass) >= min_f2p
        if measured_hard or large:
            out.append(Arc(stages=(stage,), subsystem="(single)"))
    return out


# ---------------------------------------------------------------------------
# Task content
# ---------------------------------------------------------------------------

_SLUG_NOISE = re.compile(
    r"^(fix|feat|feat!|bugfix|chore|refactor|perf|docs|test)(\([^)]*\))?!?:\s*"
)


def task_slug(arc: Arc) -> str:
    """kebab-case, <=3 tokens, derived from the arc's lead title + content hash."""
    title = _SLUG_NOISE.sub("", arc.stages[0].title.lower())
    words = re.findall(r"[a-z0-9]+", title)[:2]
    digest = hashlib.sha256(arc.base_commit.encode()).hexdigest()[:6]
    stem = "-".join(words) or "task"
    return f"{stem}-{digest}"[:60]


def build_arc_instruction(arc: Arc) -> str:
    """A self-contained spec: intent per stage + the graded test contract."""
    if len(arc.stages) == 1:
        body = arc.stages[0].instruction
    else:
        parts = [
            "This change is composed of several consecutive changes, all of which\n"
            "must work together at the end:\n"
        ]
        for stage in arc.stages:
            parts.append(f"### Part {stage.index}\n\n{stage.instruction}")
        body = "\n\n".join(parts)
    tests = "\n".join(f"- `{path}`" for path in arc.test_paths)
    return (
        f"{body}\n\n"
        "## Graded tests\n\n"
        "The change is graded by these tests (present in the workspace at these\n"
        "paths; they are the specification, so edit the source, not the tests):\n\n"
        f"{tests}\n"
    )


def build_arc_dockerfile(
    bootstrap_image: str,
    arc: Arc,
    *,
    language: str | None,
) -> str:
    """Position the repo at the arc's base commit, history scrubbed."""
    span = len(arc.stages) * 2 + 8
    depth = max(64, span * 2 + 32)
    return "".join(
        [
            f"FROM {bootstrap_image}\n",
            "WORKDIR /workspace\n",
            "RUN git config --global --add safe.directory /workspace \\\n"
            f"    && git fetch --depth {depth} origin {arc.final_commit} 2>/dev/null \\\n"
            "    || git fetch --unshallow origin 2>/dev/null || true\n",
            f"RUN git reset --hard {arc.base_commit} && git clean -fdx\n",
            git_history_scrub(arc.base_commit),
            # The graded tests at their target version are the specification;
            # the agent edits source, not tests. (The verifier restores its own
            # trusted copies at grading time regardless.)
            "COPY spec-tests/ /workspace/\n",
            # The verifier grades with CTRF in this same image (single-step
            # tasks have no separate tests image); bake the plugin exactly like
            # the chain templates do.
            "RUN uv pip install --python /opt/venv/bin/python pytest-json-ctrf==0.5.2\n",
            "ENV PYTHONDONTWRITEBYTECODE=1\n",
        ]
    )


# ---------------------------------------------------------------------------
# Validation + emission
# ---------------------------------------------------------------------------


def build_arc_test_script(test_cmds: list[str]) -> str:
    """tests/test.sh for one arc task (single gradeable run, binary reward)."""
    template = string.Template(
        _resource_files("repo2rlenv.pipelines")
        .joinpath("templates")
        .joinpath("arc_test.sh")
        .read_text(encoding="utf-8")
    )
    joined = " && ".join(test_cmds) if test_cmds else "echo 'no test_cmds'"
    # No `-p no:cacheprovider`: the repo's conftest scans argv for a profile
    # name and chokes on the plugin flag's value (observed: INTERNALERROR
    # "Invalid profile name 'no:cacheprovider'"). The cache plugin is harmless.
    ctrf_joined = " && ".join(f"{cmd} --ctrf /tmp/r2e_ctrf.json" for cmd in test_cmds)
    return template.substitute(
        TEST_CMDS=joined,
        TEST_CMDS_CTRF=ctrf_joined.replace("'", "'\\''"),
        TEST_CMDS_ESCAPED=joined.replace("'", "'\\''"),
    )


def validate_arc(
    sandbox,
    arc: Arc,
    *,
    language: str | None,
    timeout: int = 900,
    on_reject=None,
) -> Arc | None:
    """Confirm the arc's oracle: F2P fails at base, passes cleanly at final.

    Returns the arc with the graded sets pruned to what actually holds, or None
    when the arc cannot gate a binary clean-command reward. Tests run against
    the arc-final versions at both trees, which is what the task grades with.
    `on_reject(reason)` is invoked with the gate that failed, for diagnostics.
    """

    def _reject(reason: str) -> None:
        if on_reject is not None:
            on_reject(reason)
        return None

    from repo2rlenv.pipelines._pr_chain_validate import _statuses

    cmds = [f"pytest -v -n 0 {' '.join(arc.test_paths)}"]
    base_map, base_exit = _statuses(
        sandbox,
        arc.base_commit,
        cmds,
        tests_from=arc.final_commit,
        test_paths=tuple(arc.test_paths),
        language=language,
        timeout=timeout,
    )
    final_map, final_exit = _statuses(
        sandbox,
        arc.final_commit,
        cmds,
        tests_from=arc.final_commit,
        test_paths=tuple(arc.test_paths),
        language=language,
        timeout=timeout,
    )
    if not final_map:
        return _reject(f"final map empty (final_exit={final_exit}, base_exit={base_exit})")
    f2p = sorted(
        t for t in arc.fail_to_pass if final_map.get(t) == "PASSED" and base_map.get(t) != "PASSED"
    )
    p2p = sorted(
        t for t in arc.pass_to_pass if final_map.get(t) == "PASSED" and base_map.get(t) == "PASSED"
    )
    # Binary reward + clean command: the final-tree run must be clean, and
    # there must be something the task requires.
    if final_exit != 0:
        nonpass = sum(1 for v in final_map.values() if v != "PASSED")
        return _reject(f"final run dirty (exit={final_exit}, {nonpass}/{len(final_map)} non-passing)")
    if not f2p:
        return _reject("no F2P holds (all required tests already pass at base)")
    stages = []
    for i, stage in enumerate(arc.stages):
        last = i + 1 == len(arc.stages)
        stages.append(
            ArcStage(
                index=stage.index,
                pr_number=stage.pr_number,
                title=stage.title,
                instruction=stage.instruction,
                before_commit=stage.before_commit,
                after_commit=stage.after_commit,
                test_paths=stage.test_paths,
                fail_to_pass=f2p if last else [],
                pass_to_pass=p2p if last else [],
                source_paths=stage.source_paths,
                measured_reward=stage.measured_reward,
            )
        )
    return Arc(stages=tuple(stages), subsystem=arc.subsystem)


def build_arc_task(
    arc: Arc,
    *,
    clone_dir: Path,
    bootstrap_image: str,
    language: str | None,
    verifier_source: str,
    org: str,
) -> HarborTask:
    """Render one validated arc as a Terminal-Bench-conformant Harbor task."""
    name = task_slug(arc)
    test_cmds = [f"pytest -v -n 0 {' '.join(arc.test_paths)}"]

    aux: dict[str, str] = {
        "tests/verifier.py": verifier_source,
        "tests/f2p.json": json.dumps(arc.fail_to_pass, indent=2),
        "tests/p2p.json": json.dumps(arc.pass_to_pass, indent=2),
    }
    # Trusted test copies at the arc-final version — restored over the tree at
    # grading, and staged into the workspace at start (tests are the spec).
    harness_seen: set[str] = set()
    harness_ship: list[str] = []
    for rel_path in arc.test_paths:
        parts = rel_path.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            d = "/".join(parts[:i])
            candidate = f"{d}/conftest.py"
            if candidate not in harness_seen:
                harness_seen.add(candidate)
                harness_ship.append(candidate)
    harness_ship += ["pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini"]
    purge = list(harness_ship)
    for rel_path in [*arc.test_paths, *harness_ship]:
        content = file_at_commit(clone_dir, arc.final_commit, rel_path)
        if content is not None:
            aux[f"tests/files/{rel_path}"] = content
            if rel_path in arc.test_paths:
                aux[f"environment/spec-tests/{rel_path}"] = content
    purge = [p for p in purge if f"tests/files/{p}" not in aux]
    aux["tests/purge.manifest"] = "\0".join(purge) + "\0"

    stage_count = len(arc.stages)
    lead = arc.stages[0].title
    return HarborTask(
        name=name,
        org=org,
        description=f"{lead}" + (f" (+{stage_count - 1} follow-ups)" if stage_count > 1 else ""),
        instruction=build_arc_instruction(arc),
        oracle_diff=range_diff(
            clone_dir,
            arc.base_commit,
            arc.final_commit,
            # The image pre-stages the graded tests at their target version
            # (the spec); the gold patch must not re-apply them. Binary blobs
            # (infographic pngs etc.) are excluded too: the tests never read
            # them, and inlined literal deltas ballooned one patch to 68 MB.
            exclude_paths=tuple(arc.test_paths)
            + tuple(binary_changed_files(clone_dir, arc.base_commit, arc.final_commit)),
        ),
        repo2env={
            "pipeline": "pr_arc",
            "pipeline_version": "0.1.0",
            "arc_stage_count": stage_count,
            "arc_prs": [s.pr_number for s in arc.stages if s.pr_number is not None],
            "base_commit": arc.base_commit,
            "final_commit": arc.final_commit,
            "reward_mode": "binary_clean_command",
        },
        difficulty="hard",
        category="Software",
        subcategory="Software Engineering",
        tags=["bugfix", "python", "test-driven"],
        difficulty_explanation=(
            "The change is a real production change that only passes when its own "
            "tests pass, in a large live codebase whose conventions and internal APIs "
            "must be discovered. It requires the daily judgment of an engineer who "
            "maintains this class of system; the data comes from the repository's real "
            "public history."
        ),
        solution_explanation=(
            "The reference solution is the real merged change for this objective, "
            "replayed as one patch onto the base tree."
        ),
        verification_explanation=(
            "The verifier restores trusted test and pytest-harness copies (purging "
            "planted conftest/config), runs the graded tests unprivileged as nobody, "
            "and reads the runner's CTRF report rather than printed output. The reward "
            "is binary: 1 exactly when every required test passes and the command is "
            "clean (exit 0, no untracked failures)."
        ),
        expert_time_estimate_hours=2.0 + 1.5 * (stage_count - 1),
        author_name="Repo2RLEnv pr_arc",
        environment_dockerfile=build_arc_dockerfile(bootstrap_image, arc, language=language),
        test_script=build_arc_test_script(test_cmds),
        agent_timeout_sec=7_200.0,
        verifier_timeout_sec=900.0,
        aux_files={
            **aux,
            "environment/docker-compose.yaml": egress_guard_compose(),
        },
    )
