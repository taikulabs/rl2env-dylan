"""Render a validated chain as native Harbor steps.

Harbor already implements the loop a long-horizon environment needs. For each
entry in a task's `steps` array it runs, in order:

    steps/<name>/workdir/setup.sh   the state the agent starts this step from
    steps/<name>/instruction.md     the observation
    <the agent phase>               the action
    steps/<name>/tests/test.sh      the transition, which returns the reward

`min_reward` aborts the remaining steps, and `multi_step_reward_strategy="mean"`
averages the per-step rewards into the trial reward. So one chain stage becomes
one real environment step, counted and scored by the runtime rather than
simulated by anything this project ships into the container.

Note on background processes: an earlier revision killed PID-1 orphans at
the start of test.sh to stop a leftover loop from rewriting reward.txt. That
proved dangerous in practice — Harbor's own in-container helpers also show up
with PPID 1, and killing one broke the exec channel. The real fix is the
separate verifier environment (the default), where no agent process exists at
all. In shared mode the background-writer residual is accepted and documented:
shared mode is for throwaway training runs, not eval.

Two consequences of grading in place, both of which simplify the task:

* A stage's tests are restored from files shipped with *that step*, so an agent
  only ever sees the tests for the milestone it is working on — not the whole
  chain's.
* The gold patch for a stage lives in `steps/<name>/solution/`, which Harbor
  uploads for the oracle agent only. Nothing reveals it to a normal run.
"""

from __future__ import annotations

import json
import shlex
import string
from dataclasses import dataclass, field
from importlib.resources import files as _resource_files
from pathlib import Path

from repo2rlenv.emitter.harbor import HarborStep
from repo2rlenv.git_local import file_at_commit, range_diff
from repo2rlenv.pipelines._env_guard import egress_guard_compose
from repo2rlenv.pipelines._pr_chain_plan import ChainPlan, StagePlan

# Reward below which a checkpoint step aborts the rest of the chain. A stage that
# earns literally nothing means the agent is not making contact with the task.
HOPELESS_STEP_REWARD = 0.01

# The task always promises at least this many native Harbor steps. Checkpoints
# cannot end an episode before that horizon.
MINIMUM_STEPS_BEFORE_ABORT = 100

# After the minimum horizon, recheck periodically instead of gating every step.
CHECKPOINT_EVERY = 25

# Cumulative signal: every step replays the trailing few prior stages' F2P
# tests, and every tenth step replays all of them. The regression score is a
# separate reward key (Harbor averages keys independently), never blended into
# the local reward — a regression failure lowers maintenance, not the grade
# for the current stage.
REGRESSION_WINDOW = 5
REGRESSION_MILESTONE_EVERY = 10


def _regression_stages(stages: list[StagePlan], index: int) -> list[StagePlan]:
    """Prior stages whose F2P tests this step replays (deterministic).

    The final step is always a milestone — it replays every prior stage's F2P
    tests regardless of where it lands in the modulo schedule.
    """
    prior = [s for s in stages if s.index < index and s.fail_to_pass]
    last = max(s.index for s in stages)
    if index == last or index % REGRESSION_MILESTONE_EVERY == 0:
        return prior
    return prior[-REGRESSION_WINDOW:]


@dataclass(frozen=True, slots=True)
class GradingPolicy:
    """How a step is graded and what isolation the grader gets.

    `image_ref=None` is SHARED mode: the verifier runs in the agent container
    (cheap, training-only). With an image ref, Harbor grades in a separate
    environment built from the step tests Dockerfile and the agent tree crosses
    over as a /workspace artifact — the mode where a root agent cannot reach
    the grader interpreter, PATH, or reward files.
    """

    agent_timeout_sec: float
    verifier_timeout_sec: float
    checkpoint_every: int = CHECKPOINT_EVERY
    minimum_steps_before_abort: int = MINIMUM_STEPS_BEFORE_ABORT
    image_ref: str | None = None
    workspace_excludes: list[str] = field(default_factory=list)


def _template(name: str) -> string.Template:
    """Load a shell template; `$NAME` placeholders, `$$` is a literal dollar."""
    text = (
        _resource_files("repo2rlenv.pipelines")
        .joinpath("templates")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )
    return string.Template(text)


def step_name(index: int) -> str:
    """Zero-padded so `steps/` sorts correctly at three digits."""
    return f"stage-{index:03d}"


def build_step_setup_script(*, has_carry: bool) -> str:
    """`workdir/setup.sh` — put the tree into the state this step starts from.

    Carry is the project churn between the previous graded milestone and this one:
    formatting sweeps, dependency bumps, and any stage that validation could not
    grade. Applying it here rather than asking the agent for it keeps the replay
    gapless without inventing work.

    Both variants wipe `/logs/verifier` and `/tests` first. Harbor only empties
    those right before verification, so without this the agent could read the
    previous step's grader — verifier source, F2P/P2P lists, reward details —
    during this step's work phase.
    """
    name = "step_setup_carry.sh" if has_carry else "step_setup.sh"
    return _template(name).template


def _harness_paths(test_paths: list[str]) -> tuple[list[str], list[str]]:
    """Return (harness candidates, conftest purge candidates) for graded tests.

    pytest reads per-directory `conftest.py` from the rootdir down to each test
    file, and `addopts` from `pyproject.toml`/`pytest.ini`/`setup.cfg`/
    `tox.ini`. The agent controls `/workspace`, so every one of those is an
    injection point: a planted conftest can print forged PASSED lines without
    running a test, and planted addopts can load an in-repo plugin. Callers ship
    the gold version of each harness file that exists at the stage's gold commit
    and purge the rest — a `pytest.ini` planted where gold has none outranks the
    restored `pyproject.toml`, so absence must be enforced, not just presence.
    """
    dirs: set[str] = {""}  # repo root: /workspace/conftest.py + config files
    for rel in test_paths:
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))
    conftests = sorted(f"{d}/conftest.py".lstrip("/") for d in dirs)
    ship = [*conftests, "pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini"]
    return ship, conftests


def build_step_test_script(
    *,
    test_cmds: list[str],
    language: str | None,
    regression_cmds: list[str] | None = None,
) -> str:
    """`tests/test.sh` — restore this stage's tests, run them, emit the reward.

    Test and harness files are *copied* from `tests/files/` rather than patched
    in. The agent may have rewritten or deleted them, and a copy is both
    deterministic and the anti-tamper guard: a stage cannot be passed by
    weakening its tests. The copy only covers declared paths, so first a purge
    deletes every harness path the gold tree does not provide (read from
    `tests/purge.manifest`, NUL-delimited — no repo-derived path is ever
    interpolated into this script, so a filename containing backticks or `$(…)`
    is inert).
    """
    joined = " && ".join(test_cmds) if test_cmds else "echo 'no test_cmds'"
    if regression_cmds:
        reg_joined = " && ".join(regression_cmds)
        regression_block = (
            "# Cumulative check: replay earlier stages' graded tests (a separate\n"
            "# diagnostic run; it never gates the local reward).\n"
            'if [ -d "$SCRIPT_DIR/regression/files" ]; then\n'
            '  (cd "$SCRIPT_DIR/regression/files" && find . -type f -print0) | \\\n'
            '    while IFS= read -r -d "" rel; do\n'
            '      mkdir -p "/workspace/$(dirname "$rel")"\n'
            '      cp "$SCRIPT_DIR/regression/files/$rel" "/workspace/$rel"\n'
            "    done\n"
            "fi\n"
            f"( {reg_joined} ) > /logs/verifier/regression_output.log 2>&1\n"
            "REGRESSION_EXIT_CODE=$?\n"
            "cat /logs/verifier/regression_output.log\n"
        )
        regression_args = (
            '--regression "$SCRIPT_DIR/regression.json" '
            "--regression-log /logs/verifier/regression_output.log "
            '--regression-exit-code "$REGRESSION_EXIT_CODE"'
        )
    else:
        regression_block = ""
        regression_args = ""
    return _template("step_test.sh").substitute(
        PATH_PRELUDE=_path_prelude(language),
        TEST_CMDS=joined,
        TEST_CMDS_ESCAPED=joined.replace("'", "'\\''"),
        REGRESSION_BLOCK=regression_block,
        REGRESSION_ARGS=regression_args,
    )


def build_step_solve_script() -> str:
    """`solution/solve.sh` — apply this stage's gold patch.

    Harbor uploads a step's `solution/` for the oracle agent only, so this is the
    one artifact that must never be readable during a normal run.
    """
    return _template("step_solve.sh").template


def build_step_tests_dockerfile(image_ref: str) -> str:
    """`tests/Dockerfile` — the image a *separate* verifier environment runs.

    Harbor builds the separate verifier environment with the step's tests/ dir
    as the build context, so the grader (test.sh, verifier.py, the F2P/P2P lists
    and the gold harness files) is baked into that image here. Baking them into
    a verifier-only image leaks nothing: the agent's environment never sees it.

    The agent's tree arrives later as the `/workspace` artifact, so the image
    only needs the toolchain (FROM the bootstrap image) plus the grader files.
    """
    return _template("step_tests.Dockerfile").substitute(IMAGE_REF=image_ref)


def _path_prelude(language: str | None) -> str:
    """Prepend known toolchain dirs for languages installed outside /usr/bin."""
    extras = {
        "go": ["/usr/local/go/bin", "$HOME/go/bin"],
        "rust": ["$HOME/.cargo/bin"],
        "node": ["/usr/local/lib/node_modules/.bin"],
        "java": ["/usr/lib/jvm/default-java/bin"],
    }
    dirs = extras.get((language or "").lower(), [])
    return f'export PATH="{":".join(dirs)}:$PATH"\n' if dirs else ""


def build_chain_steps(
    plan: ChainPlan,
    *,
    clone_dir: Path,
    verifier_source: str,
    language: str | None,
    policy: GradingPolicy,
) -> list[HarborStep]:
    """Turn a validated plan into one Harbor step per gated stage."""
    if policy.checkpoint_every < 0:
        raise ValueError("checkpoint_every must be non-negative")
    if policy.minimum_steps_before_abort < 1:
        raise ValueError("minimum_steps_before_abort must be positive")

    image_ref = policy.image_ref
    separate = image_ref is not None
    steps: list[HarborStep] = []
    for stage in plan.stages:
        index = stage.index
        name = step_name(index)
        aux: dict[str, str] = {
            "tests/verifier.py": verifier_source,
            "tests/f2p.json": json.dumps(stage.fail_to_pass, indent=2),
            "tests/p2p.json": json.dumps(stage.pass_to_pass, indent=2),
        }

        has_carry = stage.before_commit != stage.carry_commit
        if has_carry:
            aux["workdir/carry.diff"] = range_diff(
                clone_dir, stage.before_commit, stage.carry_commit
            )
        aux["workdir/setup.sh"] = build_step_setup_script(has_carry=has_carry)

        # The graded tests, taken from this stage's gold tree. Two copies:
        # `tests/files/` feeds the verifier's restore, and `workdir/.r2e/tests/`
        # lands in the agent's workspace at step start so the agent can run the
        # exact gate while it works. Tests are the specification; the gold
        # *source* diff is what stays hidden. Measured: a blind step gates on
        # exact internal names the agent cannot guess (86% of stages here), and
        # Opus scored 0.067 mean over 39 blind steps — iteration against the
        # real tests is what makes the milestone earnable.
        for rel_path in stage.test_paths:
            content = file_at_commit(clone_dir, stage.after_commit, rel_path)
            if content is not None:
                aux[f"tests/files/{rel_path}"] = content
                aux[f"workdir/.r2e/tests/{rel_path}"] = content

        # The harness those tests run under: the gold conftest chain plus the
        # pytest config files. A candidate the gold tree HAS is restored from
        # the gold copy; one it LACKS goes on the purge manifest, so a planted
        # pytest.ini (which outranks pyproject.toml) cannot survive grading.
        harness_candidates, conftest_purge = _harness_paths(list(stage.test_paths))
        purge: list[str] = list(conftest_purge)
        for rel_path in harness_candidates:
            content = file_at_commit(clone_dir, stage.after_commit, rel_path)
            if content is not None:
                aux[f"tests/files/{rel_path}"] = content
            elif rel_path not in purge:
                purge.append(rel_path)
        # NUL-delimited: repo-controlled filenames never enter the script text.
        aux["tests/purge.manifest"] = "\0".join(purge) + "\0"

        # The separate verifier environment builds with this step's tests/ dir
        # as its context and does not inherit the task's compose overlay — so
        # it carries its own copy of the denylist. Agent-authored code runs
        # there during grading, and this closes the question of what it can
        # reach while it does.
        if separate:
            aux["tests/docker-compose.yaml"] = egress_guard_compose()

        # The gold source patch for this stage only — oracle agent territory.
        aux["solution/patch.diff"] = range_diff(clone_dir, stage.carry_commit, stage.after_commit)

        tests_block = (
            "\n\n## Graded tests\n\n"
            "This stage is graded by these tests (already in your workspace at "
            "these paths; they were overwritten with the project copy when the "
            "stage opened, so edit the source, not the tests):\n\n"
            + "\n".join(f"- `{path}`" for path in stage.test_paths)
        )
        # Cumulative maintenance check: replay selected earlier stages' F2P
        # tests against the tree as this step leaves it. Test file content comes
        # from THIS stage's start commit (carry_commit) — the version matching
        # the tree the tests run against. A file absent there is skipped (the
        # behavior did not exist yet at the chain's earlier point is impossible:
        # carry_commit is after the prior stage's gold).
        regression_ids: list[str] = []
        regression_cmds: list[str] = []
        for prior in _regression_stages(plan.stages, index):
            regression_ids.extend(prior.fail_to_pass)
            for rel_path in prior.test_paths:
                content = file_at_commit(clone_dir, stage.carry_commit, rel_path)
                if content is not None:
                    aux[f"tests/regression/files/{rel_path}"] = content
        if regression_ids:
            aux["tests/regression.json"] = json.dumps(sorted(set(regression_ids)))
            regression_paths = sorted(
                {k.split("::")[0] for k in regression_ids if "::" in k}
                | {k for k in regression_ids if "::" not in k}
            )
            regression_cmds = [
                "pytest -v -n 0 " + " ".join(shlex.quote(p) for p in regression_paths)
            ]

        steps.append(
            HarborStep(
                name=name,
                instruction=stage.instruction + tests_block,
                test_script=build_step_test_script(
                    test_cmds=list(stage.test_cmds),
                    language=language,
                    regression_cmds=regression_cmds or None,
                ),
                solve_script=build_step_solve_script(),
                aux_files=aux,
                agent_timeout_sec=policy.agent_timeout_sec,
                verifier_timeout_sec=policy.verifier_timeout_sec,
                min_reward=(
                    HOPELESS_STEP_REWARD
                    if policy.checkpoint_every > 0
                    and index >= policy.minimum_steps_before_abort
                    and (index - policy.minimum_steps_before_abort) % policy.checkpoint_every == 0
                    else None
                ),
                verifier_environment_mode="separate" if separate else None,
                tests_dockerfile=(
                    build_step_tests_dockerfile(image_ref) if image_ref is not None else None
                ),
                artifacts=(
                    [{"source": "/workspace", "exclude": policy.workspace_excludes}]
                    if separate
                    else []
                ),
            )
        )
    return steps
