"""Unit tests for the pr_chain pipeline.

Covers the chain graph (segments, windows, selection), the four-tree oracle
conditions, the plan instruction gate, the native-step emission contract
(step count, gold harness restore, purge manifest, separate-verifier material,
checkpoint placement), the stage-validation cache, and the generated shell
(bash -n + shellcheck over the rendered templates).
"""

from __future__ import annotations

import itertools
import json
from dataclasses import replace

import pytest

from repo2rlenv.bootstrap.docker import ExecResult
from repo2rlenv.git_local import FirstParentCommit
from repo2rlenv.pipelines._pr_chain_graph import (
    AnchorLimits,
    CarryLimits,
    Chain,
    ChainShape,
    ChainStage,
    HistoryStep,
    build_chains,
    partition_into_segments,
    subsystem_of,
)
from repo2rlenv.pipelines._pr_chain_steps import (
    GradingPolicy,
    _harness_paths,
    build_chain_steps,
    build_step_setup_script,
    build_step_solve_script,
    build_step_test_script,
    step_name,
)
from repo2rlenv.pipelines._pr_chain_validate import (
    ChainStatus,
    ChainValidation,
    StageStatus,
    StageValidation,
    _StageTrees,
    _statuses,
)
from repo2rlenv.pipelines.pr_chain import (
    PRChainPipeline,
    build_chain_instruction,
    build_chain_plan,
    build_stage_instruction,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def make_step(
    sha: str,
    *,
    parent: str,
    subject: str = "fix(cron): thing",
    source: tuple[str, ...] = ("cron/scheduler.py",),
    tests: tuple[str, ...] = ("tests/cron/test_scheduler.py",),
    lines: int = 100,
    pr: int | None = 1,
) -> HistoryStep:
    return HistoryStep(
        commit=FirstParentCommit(
            sha=sha,
            parent_sha=parent,
            subject=subject,
            committed_at="2026-01-01T00:00:00Z",
            is_merge=False,
        ),
        source_paths=source,
        test_paths=tests,
        lines_changed=lines,
        pr_number=pr,
    )


def linear_steps(count: int, **kwargs) -> list[HistoryStep]:
    """`count` consecutive anchor steps: c1 parented on c0, c2 on c1, ..."""
    return [make_step(f"c{i + 1}", parent=f"c{i}", pr=100 + i, **kwargs) for i in range(count)]


def make_stage(index: int, *, source_count: int = 2, subsystem: str = "cron") -> ChainStage:
    return ChainStage(
        index=index,
        pr_number=1000 + index,
        title=f"fix: thing {index}",
        before_commit=f"b{index}",
        carry_commit=f"b{index}",
        after_commit=f"a{index}",
        carry_shas=(),
        carry_lines_changed=0,
        source_paths=tuple(f"src/f{index}_{n}.py" for n in range(source_count)),
        test_paths=(f"tests/test_{index}.py",),
        lines_changed=50,
        subsystem=subsystem,
    )


# ---------------------------------------------------------------------------
# subsystem attribution
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("cron/scheduler.py", "cron"),
        # A test path maps onto the subsystem it exercises, not onto "tests",
        # so a stage's source and test changes agree on one subsystem.
        ("tests/cron/test_scheduler.py", "cron"),
        ("tests/gateway/relay/test_x.py", "gateway"),
        # Monorepo roots hold many components; the component is one level deeper.
        ("apps/desktop/src/main.ts", "apps/desktop"),
        ("packages/core/index.ts", "packages/core"),
        # A bare root file has no subsystem.
        ("README.md", "(root)"),
        ("", "(root)"),
    ],
)
def test_subsystem_of(path: str, expected: str) -> None:
    assert subsystem_of(path) == expected


# ---------------------------------------------------------------------------
# stage partition
# ---------------------------------------------------------------------------


def test_partition_is_gapless() -> None:
    """Stage k must start exactly where stage k-1 ended.

    This is the property that makes a chain replayable: any gap means stage k
    begins from a tree that never existed in history.
    """
    segments = partition_into_segments(linear_steps(5), AnchorLimits(), CarryLimits())
    assert len(segments) == 1
    stages = segments[0]
    assert len(stages) == 5
    for previous, current in itertools.pairwise(stages):
        assert current.before_commit == previous.after_commit


def test_non_anchor_steps_are_carried_not_dropped() -> None:
    """A docs-only commit becomes free carry, and the partition stays gapless."""
    steps = [
        make_step("c1", parent="c0", pr=1),
        # No test change -> cannot anchor a stage.
        make_step("c2", parent="c1", source=("docs/x.md",), tests=(), pr=2),
        make_step("c3", parent="c2", pr=3),
    ]
    stages = partition_into_segments(steps, AnchorLimits(), CarryLimits())[0]
    assert len(stages) == 2
    carried = stages[1]
    assert carried.carry_shas == ("c2",)
    assert carried.has_carry
    # before -> carry covers the free churn; carry -> after is the graded goal.
    assert carried.before_commit == "c1"
    assert carried.carry_commit == "c2"
    assert carried.after_commit == "c3"


def test_carry_over_budget_creates_a_barrier() -> None:
    """An unshippable carry splits the history instead of bloating a stage.

    The anchor that would have carried the oversized churn (c3) is dropped with
    it: shipping its stage would mean shipping a 500k-line diff into the task.
    The next stage still starts from a real commit, so nothing is left dangling.
    """
    steps = [
        make_step("c1", parent="c0", pr=1),
        make_step("c2", parent="c1", source=("uv.lock",), tests=(), lines=500_000, pr=2),
        make_step("c3", parent="c2", pr=3),
        make_step("c4", parent="c3", pr=4),
    ]
    segments = partition_into_segments(steps, AnchorLimits(), CarryLimits())
    assert [len(s) for s in segments] == [1, 1]
    # No chain spans the barrier, and the stage after it starts at a real commit.
    assert segments[0][-1].after_commit == "c1"
    assert segments[1][0].before_commit == "c3"
    assert segments[1][0].after_commit == "c4"
    assert segments[1][0].carry_shas == ()


@pytest.mark.parametrize(
    "subject",
    [
        "fmt(js): `npm run fix` on merge",
        "style: reformat everything",
        "chore(lint): ruff format",
        "backport: fix from stable",
        'Revert "feat: thing"',
    ],
)
def test_unusable_subjects_do_not_anchor_a_stage(subject: str) -> None:
    """Formatting sweeps and backports cannot be milestones.

    Reproducing a formatter's exact output is not a solvable objective, and such
    a change moves no test, so no fail-to-pass oracle can exist for it.
    """
    steps = [make_step("c1", parent="c0", subject=subject, pr=1)]
    assert partition_into_segments(steps, AnchorLimits(), CarryLimits()) == []


def test_anchor_requires_both_source_and_test_changes() -> None:
    source_only = [make_step("c1", parent="c0", tests=(), pr=1)]
    test_only = [make_step("c1", parent="c0", source=(), pr=1)]
    assert partition_into_segments(source_only, AnchorLimits(), CarryLimits()) == []
    assert partition_into_segments(test_only, AnchorLimits(), CarryLimits()) == []


def test_require_pr_link_rejects_unattributed_steps() -> None:
    steps = [make_step("c1", parent="c0", pr=None)]
    assert partition_into_segments(steps, AnchorLimits(require_pr_link=True), CarryLimits()) == []
    assert partition_into_segments(steps, AnchorLimits(require_pr_link=False), CarryLimits())


# ---------------------------------------------------------------------------
# chain selection
# ---------------------------------------------------------------------------


def test_chain_needs_both_floor_and_stage_minimum() -> None:
    """One large commit clearing the floor is not a long-horizon environment."""
    segment = (make_stage(1, source_count=200),)
    selection = build_chains(
        [segment], shape=ChainShape(min_action_floor=100, min_stages=8), target_count=5
    )
    assert selection.chains == ()
    assert selection.rejected_short_horizon == 1


def test_selected_chain_meets_the_declared_floor() -> None:
    segment = tuple(make_stage(i + 1, source_count=3) for i in range(40))
    selection = build_chains(
        [segment],
        shape=ChainShape(min_action_floor=100, min_stages=8),
        target_count=1,
        overlap_ladder=(0.0,),
    )
    (chain,) = selection.chains
    assert chain.action_floor >= 100
    assert len(chain.stages) >= 8
    # Stages are renumbered per chain so a task's stages read 1..N.
    assert [s.index for s in chain.stages] == list(range(1, len(chain.stages) + 1))


def test_first_rung_yields_only_disjoint_chains() -> None:
    """Rung 0.0 must never let two chains share a stage."""
    segment = tuple(make_stage(i + 1, source_count=3) for i in range(80))
    disjoint = build_chains(
        [segment],
        shape=ChainShape(min_action_floor=100, min_stages=8),
        target_count=100,
        overlap_ladder=(0.0,),
    )
    assert disjoint.max_stage_reuse == 1
    assert disjoint.overlap_fraction_used == 0.0
    # 80 stages at floor 5 each fit four 20-stage chains and no more.
    assert len(disjoint.chains) == 4


def test_overlap_rung_is_entered_only_when_the_target_is_unmet() -> None:
    """The ladder must not spend overlap it does not need.

    A request the segment satisfies disjointly stays on rung 0.0; a request it
    cannot climbs, and the reported rung says which was used.
    """
    segment = tuple(make_stage(i + 1, source_count=3) for i in range(80))
    satisfied = build_chains(
        [segment],
        shape=ChainShape(min_action_floor=100, min_stages=8),
        target_count=2,
        overlap_ladder=(0.0, 0.5),
    )
    assert len(satisfied.chains) == 2
    assert satisfied.overlap_fraction_used == 0.0

    unsatisfied = build_chains(
        [segment],
        shape=ChainShape(min_action_floor=100, min_stages=8),
        target_count=100,
        overlap_ladder=(0.0, 0.5),
    )
    assert unsatisfied.overlap_fraction_used == 0.5
    # Even the top rung refuses a window whose history is already fully claimed,
    # so the yield is capped rather than filled with duplicate chains.
    assert len(unsatisfied.chains) >= len(satisfied.chains)
    assert unsatisfied.max_stage_reuse == 1


def test_coherence_floor_filters_scattered_windows() -> None:
    mixed = tuple(make_stage(i + 1, source_count=3, subsystem=f"sub{i % 8}") for i in range(40))
    assert (
        build_chains(
            [mixed], shape=ChainShape(min_action_floor=100, min_stages=8, min_coherence=0.9)
        ).chains
        == ()
    )
    assert build_chains(
        [mixed], shape=ChainShape(min_action_floor=100, min_stages=8, min_coherence=0.0)
    ).chains


def test_overlap_fraction_must_be_a_fraction() -> None:
    with pytest.raises(ValueError, match="overlap fractions"):
        build_chains([(make_stage(1),)], overlap_ladder=(1.0,))


# ---------------------------------------------------------------------------
# plan + payload
# ---------------------------------------------------------------------------


def _chain_of(stage_count: int) -> Chain:
    stages = tuple(make_stage(i + 1) for i in range(stage_count))
    return Chain(
        base_commit=stages[0].before_commit,
        head_commit=stages[-1].after_commit,
        stages=stages,
        subsystem="cron",
        coherence=1.0,
    )


def _validation_of(chain: Chain, *, unverified: set[int] = frozenset()) -> ChainValidation:
    return ChainValidation(
        status=ChainStatus.VERIFIED,
        stages=[
            StageValidation(
                index=stage.index,
                status=StageStatus.NO_ORACLE if stage.index in unverified else StageStatus.VERIFIED,
                test_cmds=["pytest -v"],
                fail_to_pass=[] if stage.index in unverified else [f"tests/t.py::s{stage.index}"],
                pass_to_pass=["tests/t.py::keep"],
            )
            for stage in chain.stages
        ],
    )


def test_plan_drops_unverified_stages_and_renumbers() -> None:
    """A stage whose change moved no test cannot be graded, so it is not shipped."""
    chain = _chain_of(5)
    plan = build_chain_plan(
        chain,
        _validation_of(chain, unverified={2, 4}),
        repo="o/n",
        stage_instructions={i: f"do {i}" for i in range(1, 6)},
        base_test_cmds=["pytest -v"],
    )
    assert [s.index for s in plan.stages] == [1, 2, 3]
    assert [s.after_commit for s in plan.stages] == ["a1", "a3", "a5"]
    assert all(s.fail_to_pass for s in plan.stages)


def test_stage_instruction_strips_solution_leaks() -> None:
    stage = make_stage(1)
    text = build_stage_instruction(
        stage,
        title="fix: drop duplicate replies",
        body="Cherry-pick 0123456789abcdef from #4321 and rerun tests/test_x.py",
    )
    assert "fix: drop duplicate replies" in text
    assert "0123456789abcdef" not in text


# ---------------------------------------------------------------------------
# reward
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# contract
# ---------------------------------------------------------------------------


def test_pipeline_declares_bootstrap_and_pull_requests() -> None:
    from repo2rlenv.sources import Capability

    assert PRChainPipeline.requires_bootstrap is True
    assert Capability.PULL_REQUESTS in PRChainPipeline.required_capabilities
    assert PRChainPipeline.name.value == "pr_chain"


def test_pipeline_refuses_to_run_without_a_bootstrap_image() -> None:
    """Stages are graded by running the repo's tests, which needs the image."""
    with pytest.raises(RuntimeError, match="requires a BootstrapResult"):
        PRChainPipeline(input=None, options=None, bootstrap=None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# strict oracle conditions
# ---------------------------------------------------------------------------


def _trees(base: str, start: str, gold: str, head: str) -> _StageTrees:
    """One test's status on each of the four trees the reward depends on."""
    return _StageTrees(
        base={"t": base},
        start={"t": start},
        gold={"t": gold},
        head={"t": head},
    )


def test_fail_to_pass_requires_failing_at_the_chain_base() -> None:
    """A test already passing at the base pays a do-nothing agent.

    This is the defect that scored an untouched tree 0.111 on hermes-agent: the
    oracle was derived from stage-era test files but graded with the head's, so
    tests that were broken in their old form already passed in their final one.
    """
    passing_at_base = _trees("PASSED", "FAILED", "PASSED", "PASSED")
    assert not passing_at_base.is_fail_to_pass("t")


def test_fail_to_pass_requires_failing_where_the_stage_opens() -> None:
    """A test already passing when the stage opens asks for no work."""
    assert not _trees("FAILED", "PASSED", "PASSED", "PASSED").is_fail_to_pass("t")


def test_fail_to_pass_requires_passing_at_the_stage_gold_tree() -> None:
    """The native step grader requires the stage's own change to fix the test."""
    assert not _trees("FAILED", "FAILED", "FAILED", "PASSED").is_fail_to_pass("t")


def test_fail_to_pass_requires_passing_at_the_chain_head() -> None:
    """The whole-chain oracle must preserve the behavior."""
    assert not _trees("FAILED", "FAILED", "PASSED", "FAILED").is_fail_to_pass("t")


def test_fail_to_pass_accepts_a_test_broken_at_the_start_and_fixed_at_the_end() -> None:
    assert _trees("FAILED", "FAILED", "PASSED", "PASSED").is_fail_to_pass("t")


def test_a_test_absent_at_the_start_counts_as_failing() -> None:
    """A test the chain adds is the commonest fail-to-pass shape."""
    added = _StageTrees(base={}, start={}, gold={"t": "PASSED"}, head={"t": "PASSED"})
    assert added.is_fail_to_pass("t")


def test_pass_to_pass_requires_passing_everywhere() -> None:
    assert _trees("PASSED", "PASSED", "PASSED", "PASSED").is_pass_to_pass("t")
    for broken in range(4):
        statuses = ["PASSED"] * 4
        statuses[broken] = "FAILED"
        assert not _trees(*statuses).is_pass_to_pass("t")


def test_fail_to_pass_and_pass_to_pass_are_disjoint() -> None:
    """No test may be both an objective and a regression guard."""
    for combo in itertools.product(["PASSED", "FAILED"], repeat=4):
        trees = _trees(*combo)
        assert not (trees.is_fail_to_pass("t") and trees.is_pass_to_pass("t"))


def test_timed_out_test_output_never_becomes_an_oracle() -> None:
    """Partial pytest output is not a complete or trustworthy status map."""

    class TimedOutSandbox:
        def exec(self, _command: str, *, timeout: int) -> ExecResult:
            return ExecResult(
                exit_code=124,
                stdout=(
                    "R2E_START_TEST_OUTPUT\n"
                    "tests/test_one.py::test_one PASSED\n"
                    "R2E_END_TEST_OUTPUT\n"
                ),
                stderr="",
                duration_sec=float(timeout),
                timed_out=True,
            )

    statuses = _statuses(
        TimedOutSandbox(),  # type: ignore[arg-type]
        "abc123",
        ["pytest -v"],
        tests_from="def456",
        test_paths=("tests/test_one.py",),
        language="python",
        timeout=900,
    )
    assert statuses == {}


# ---------------------------------------------------------------------------
# instruction quality gate
# ---------------------------------------------------------------------------


def test_plan_drops_stages_without_a_real_problem_statement() -> None:
    """A stage whose PR carried only a title gives the agent nothing to work from."""
    chain = _chain_of(4)
    instructions = {
        1: "**fix: thing** " + " ".join(["word"] * 30),
        2: "**fix: bare title only**",
        3: "**fix: another** " + " ".join(["word"] * 30),
        4: "**short**",
    }
    plan = build_chain_plan(
        chain,
        _validation_of(chain),
        repo="o/n",
        stage_instructions=instructions,
        base_test_cmds=["pytest -v"],
        min_instruction_words=12,
    )
    assert [s.after_commit for s in plan.stages] == ["a1", "a3"]
    assert [s.index for s in plan.stages] == [1, 2]


def test_plan_keeps_every_stage_when_the_gate_is_off() -> None:
    chain = _chain_of(3)
    plan = build_chain_plan(
        chain,
        _validation_of(chain),
        repo="o/n",
        stage_instructions=dict.fromkeys((1, 2, 3), "tiny"),
        base_test_cmds=["pytest -v"],
    )
    assert len(plan.stages) == 3


# ---------------------------------------------------------------------------
# native Harbor steps — one stage becomes one environment transition
# ---------------------------------------------------------------------------


def _plan_of(stage_count: int, monkeypatch) -> tuple[dict, Chain]:
    chain = _chain_of(stage_count)
    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.file_at_commit",
        lambda clone_dir, commit, path: f"# {path} @ {commit}\n",
    )
    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.range_diff",
        lambda clone_dir, before, after: f"diff {before}..{after}\n",
    )
    plan = build_chain_plan(
        chain,
        _validation_of(chain),
        repo="o/n",
        stage_instructions={i: f"objective {i} " + "word " * 20 for i in range(1, stage_count + 1)},
        base_test_cmds=["pytest -v"],
    )
    return plan, chain


def test_every_stage_becomes_one_harbor_step(monkeypatch, tmp_path) -> None:
    """Step count IS stage count — that is what makes the horizon countable.

    Harbor runs one agent phase and one verifier per entry in `steps`, so a
    100-stage chain is a 100-transition environment by construction rather than
    by an estimate of how many actions an agent might take.
    """
    plan, _ = _plan_of(100, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="# verifier\n",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    assert len(steps) == 100
    assert [s.name for s in steps] == [step_name(i) for i in range(1, 101)]


def test_each_step_ships_its_own_oracle_and_graded_tests(monkeypatch, tmp_path) -> None:
    """A step carries everything its transition needs, and nothing from others."""
    plan, _ = _plan_of(3, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="# verifier\n",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    first = steps[0]
    assert json.loads(first.aux_files["tests/f2p.json"]) == ["tests/t.py::s1"]
    assert "tests/verifier.py" in first.aux_files
    # The graded tests are copied over the tree, so weakening them cannot help.
    assert 'cp "$SCRIPT_DIR/files/$rel"' in first.test_script
    # Gold lives under solution/, which Harbor uploads for the oracle agent only.
    assert first.solve_script is not None
    assert "solution/patch.diff" in first.aux_files
    # No other stage's material leaks into this step.
    assert not any("stage-002" in key or "stage-003" in key for key in first.aux_files)


def test_step_ships_and_restores_the_gold_test_harness(monkeypatch, tmp_path) -> None:
    """The graded tests' conftest chain and pytest config come from the gold tree.

    A planted conftest.py or addopts line could otherwise fabricate results in
    the shared verifier container.
    """
    plan, _ = _plan_of(2, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    first = steps[0]
    # No repo-derived path is interpolated into the generated shell: the purge
    # list rides in a NUL-delimited manifest the script reads with read -d ''.
    assert "/workspace/conftest.py" not in first.test_script
    assert 'read -r -d "" rel' in first.test_script
    assert "purge.manifest" in first.test_script
    manifest = first.aux_files["tests/purge.manifest"]
    entries = [e for e in manifest.split("\0") if e]
    assert "conftest.py" in entries
    assert "tests/conftest.py" in entries
    # Gold harness files ship so the purge cannot strip a fixture the tests need.
    assert "tests/files/conftest.py" in first.aux_files
    assert "tests/files/tests/conftest.py" in first.aux_files
    assert "tests/files/pyproject.toml" in first.aux_files
    # The grader runs without site customization, and its crash fails closed.
    assert "python3 -S " in first.test_script
    assert 'echo "0.0" > /logs/verifier/reward.txt' in first.test_script
    # No process-kill heuristics: in the separate verifier environment no agent
    # process exists, and in Harbor's own exec namespace a PPID==1 kill list
    # hits Harbor helpers. The separate environment is the real boundary.
    assert "/proc/" not in first.test_script


def test_step_setup_hides_the_previous_grader(monkeypatch, tmp_path) -> None:
    """setup.sh removes the last step's verifier before this step's agent phase."""
    plan, _ = _plan_of(2, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    for step in steps:
        assert "rm -rf /logs/verifier /tests" in step.aux_files["workdir/setup.sh"]


def test_carry_is_applied_by_step_setup_not_asked_of_the_agent(monkeypatch, tmp_path) -> None:
    """Unrelated churn is replayed in `workdir/setup.sh` before the agent runs."""
    plan, _ = _plan_of(3, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    # Stage 1 opens on the chain base, so it has nothing carried.
    assert "no carried history" in steps[0].aux_files["workdir/setup.sh"]
    # Later stages resume from the previous stage's gold commit.
    later = steps[1]
    assert "workdir/carry.diff" in later.aux_files
    assert "git apply" in later.aux_files["workdir/setup.sh"]


def test_checkpoint_never_aborts_before_minimum_horizon(monkeypatch, tmp_path) -> None:
    """A hopeless run can stop only after the promised 100 steps."""
    plan, _ = _plan_of(106, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
            checkpoint_every=25,
            minimum_steps_before_abort=100,
        ),
    )
    assert all(step.min_reward is None for step in steps[:99])
    gated = [step.name for step in steps if step.min_reward is not None]
    assert gated == [step_name(100)]
    assert steps[99].min_reward == 0.01

    ungated = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
            checkpoint_every=0,
            minimum_steps_before_abort=100,
        ),
    )
    assert all(step.min_reward is None for step in ungated)


def test_writer_emits_the_layout_harbor_discovers(tmp_path, monkeypatch) -> None:
    """Harbor finds steps by path convention, so the paths are the contract."""
    from repo2rlenv.emitter.harbor import HarborTask, write_harbor_task

    plan, _chain = _plan_of(2, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="# v\n",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
            image_ref="img:1",
            workspace_excludes=[".git"],
        ),
    )
    task = HarborTask(
        name="t",
        org="o",
        description="d",
        instruction="top-level briefing",
        oracle_diff="diff",
        repo2env={},
        environment_dockerfile="FROM x\n",
        steps=steps,
        multi_step_reward_strategy="mean",
    )
    path = write_harbor_task(task, tmp_path / "out")
    for index in (1, 2):
        step_dir = path / "steps" / step_name(index)
        assert (step_dir / "instruction.md").is_file()
        assert (step_dir / "tests" / "test.sh").is_file()
        assert (step_dir / "solution" / "solve.sh").is_file()
        assert (step_dir / "workdir" / "setup.sh").is_file()
    import tomllib

    config = tomllib.loads((path / "task.toml").read_text())
    assert config["multi_step_reward_strategy"] == "mean"
    assert [s["name"] for s in config["steps"]] == [step_name(1), step_name(2)]
    # Separate-verifier contract: per-step grader image + workspace artifact.
    for index in (1, 2):
        dockerfile = (path / "steps" / step_name(index) / "tests" / "Dockerfile").read_text()
        assert "\nFROM img:1\n" in dockerfile
        assert "COPY . /tests" in dockerfile
    for entry in config["steps"]:
        assert entry["verifier"]["environment_mode"] == "separate"
        assert entry["artifacts"] == [{"source": "/workspace", "exclude": [".git"]}]
        # The verifier env does not inherit the task's compose overlay, so the
        # denylist ships in the step's own build context.
        compose = (path / "steps" / entry["name"] / "tests" / "docker-compose.yaml").read_text()
        assert "pypi.org:0.0.0.0" in compose
        assert "github.com:::" in compose  # IPv6 unspecified as well


def test_shared_mode_omits_the_separate_verifier_material(monkeypatch, tmp_path) -> None:
    """No image_ref: steps stay shared-mode, with no verifier Dockerfile."""
    plan, _ = _plan_of(2, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    for step in steps:
        assert step.verifier_environment_mode is None
        assert step.tests_dockerfile is None
        assert step.artifacts == []


def test_task_toml_carries_the_network_policy(tmp_path) -> None:
    """The allowlist + verifier no-network policy must survive emission."""
    import tomllib

    from repo2rlenv.emitter.harbor import HarborTask, write_harbor_task

    task = HarborTask(
        name="t",
        org="o",
        description="d",
        instruction="i",
        oracle_diff="diff",
        repo2env={},
        environment_dockerfile="FROM x\n",
        environment_network_mode="allowlist",
        environment_allowed_hosts=["api.anthropic.com"],
        verifier_network_mode="no-network",
    )
    path = write_harbor_task(task, tmp_path / "out")
    config = tomllib.loads((path / "task.toml").read_text())
    assert config["environment"]["network_mode"] == "allowlist"
    assert config["environment"]["allowed_hosts"] == ["api.anthropic.com"]
    assert config["verifier"]["network_mode"] == "no-network"


def test_task_toml_omits_network_policy_by_default(tmp_path) -> None:
    """Other pipelines keep Harbor's default (public) posture."""
    import tomllib

    from repo2rlenv.emitter.harbor import HarborTask, write_harbor_task

    task = HarborTask(
        name="t",
        org="o",
        description="d",
        instruction="i",
        oracle_diff="diff",
        repo2env={},
    )
    path = write_harbor_task(task, tmp_path / "out")
    config = tomllib.loads((path / "task.toml").read_text())
    assert "environment" not in config
    assert "network_mode" not in config["verifier"]


def test_harness_paths_cover_root_and_each_parent_dir() -> None:
    ship, purge = _harness_paths(["tests/a/b/test_x.py"])
    assert purge == [
        "conftest.py",
        "tests/a/b/conftest.py",
        "tests/a/conftest.py",
        "tests/conftest.py",
    ]
    assert purge[0] == "conftest.py"
    for cfg in ("pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini"):
        assert cfg in ship
    assert set(purge) <= set(ship)


def test_checkpoints_are_disabled_by_default() -> None:
    """The default config must not give the agent a quit-while-ahead lever."""
    from repo2rlenv.spec.options import PRChainOptions

    assert PRChainOptions().hopeless_checkpoint_every == 0


def test_harbor_mean_divides_by_executed_steps_only() -> None:
    """Pin the divisor our abort semantics depend on (harbor#2783).

    If Harbor ever divides by *declared* steps instead, the min_reward abort
    stops being a quit-while-ahead lever and can be re-enabled by default.
    """
    harbor = pytest.importorskip("harbor.trial.multi_step", reason="harbor not installed")
    from harbor.models.verifier.result import VerifierResult

    trial = harbor.MultiStepTrial.__new__(harbor.MultiStepTrial)

    class _Step:
        def __init__(self, rewards):
            self.verifier_result = None if rewards is None else VerifierResult(rewards=rewards)

    class _Result:
        pass

    trial._result = _Result()
    trial._result.step_results = [
        _Step({"reward": 0.8}),  # executed
        _Step(None),  # aborted before verification
    ]
    aggregated = trial._aggregate_step_rewards()
    assert aggregated is not None
    # Executed-only divisor: 0.8/1, not 0.8/2. If this starts failing because
    # Harbor fixed the divisor, revisit hopeless_checkpoint_every's default.
    assert aggregated.rewards["reward"] == 0.8


def test_shared_mode_requires_the_unsafe_flag_and_stamps_metadata(monkeypatch, tmp_path) -> None:
    """Shared grading is the unsafe opt-in: no isolation material, stamped."""
    from repo2rlenv.bootstrap.spec import BootstrapResult, LanguageHint
    from repo2rlenv.spec.input import GenerationInput
    from repo2rlenv.spec.options import PRChainOptions

    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.file_at_commit",
        lambda clone_dir, commit, path: f"# {path}\n",
    )
    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.range_diff",
        lambda clone_dir, before, after: f"diff {before}..{after}\n",
    )
    monkeypatch.setattr(
        "repo2rlenv.pipelines.pr_chain.range_diff",
        lambda clone_dir, before, after: f"diff {before}..{after}\n",
    )
    monkeypatch.setattr("repo2rlenv.pipelines.pr_chain._module_source", lambda name: "# v\n")

    def build(unsafe: bool):
        gen = GenerationInput.model_validate(
            {
                "repo": {"url": "o/n"},
                "pipeline": {"name": "pr_chain"},
                "output": {"destination": "./out", "org": "o", "dataset_name": "d"},
            }
        )
        bootstrap = BootstrapResult(
            image_tag="img:1",
            image_digest="sha256:x",
            language=LanguageHint.PYTHON,
            repo="o/n",
            ref="HEAD",
            rebuild_cmds=[],
            test_cmds=["pytest -v"],
            smoke_passed=True,
            iterations=1,
            build_time_sec=0.0,
            llm_provider="none",
        )
        opts = PRChainOptions(unsafe_shared_verifier=unsafe)
        pipe = PRChainPipeline(gen, opts, bootstrap)
        plan, chain = _plan_of(100, monkeypatch)
        return pipe._build_task(chain, plan, tmp_path, task_id="t")

    safe = build(False)
    assert safe.steps[0].verifier_environment_mode == "separate"
    assert safe.repo2env["eval_trustworthy"] is True

    unsafe = build(True)
    assert unsafe.steps[0].verifier_environment_mode is None
    assert unsafe.steps[0].tests_dockerfile is None
    assert unsafe.repo2env["eval_trustworthy"] is False


def test_gold_absent_pytest_ini_is_purged(monkeypatch, tmp_path) -> None:
    """A planted pytest.ini must not survive grading when gold has none.

    pytest.ini outranks pyproject.toml, so restoring only what gold *has* leaves
    an injection lane open; absence has to be enforced.
    """

    def no_configs(clone_dir, commit, path):
        if path in ("pytest.ini", "setup.cfg", "tox.ini"):
            return None
        return f"# {path}\n"

    monkeypatch.setattr("repo2rlenv.pipelines._pr_chain_steps.file_at_commit", no_configs)
    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.range_diff",
        lambda clone_dir, before, after: "diff\n",
    )
    plan = build_chain_plan(
        _chain_of(1),
        _validation_of(_chain_of(1)),
        repo="o/n",
        stage_instructions={1: "objective " + "word " * 20},
        base_test_cmds=["pytest -v"],
    )
    (step,) = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    manifest = [e for e in step.aux_files["tests/purge.manifest"].split("\0") if e]
    assert "pytest.ini" in manifest
    assert "tests/files/pytest.ini" not in step.aux_files


def test_hostile_filename_never_enters_generated_shell(monkeypatch, tmp_path) -> None:
    """A repo path with backticks/$( ) is data in the manifest, never code."""
    evil = "tests/evil_`id`_$(touch pwned)/conftest.py"
    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.file_at_commit",
        lambda clone_dir, commit, path: None,
    )
    monkeypatch.setattr(
        "repo2rlenv.pipelines._pr_chain_steps.range_diff",
        lambda clone_dir, before, after: "diff\n",
    )
    plan = build_chain_plan(
        _chain_of(1),
        _validation_of(_chain_of(1)),
        repo="o/n",
        stage_instructions={1: "objective " + "word " * 20},
        base_test_cmds=["pytest -v"],
    )
    plan = replace(
        plan,
        stages=[
            replace(
                plan.stages[0],
                test_paths=["tests/evil_`id`_$(touch pwned)/test_x.py"],
            )
        ],
    )
    (step,) = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
        ),
    )
    # The hostile path is nowhere in the script...
    assert "evil_" not in step.test_script
    # ...but the purge manifest carries it byte-for-byte.
    assert evil in step.aux_files["tests/purge.manifest"].split("\0")


def test_all_generated_shell_parses(monkeypatch, tmp_path) -> None:
    """bash -n over every generated script: generation must never emit syntax
    errors, which string-built shell is prone to."""
    import subprocess

    plan, _ = _plan_of(3, monkeypatch)
    steps = build_chain_steps(
        plan,
        clone_dir=tmp_path,
        verifier_source="# v\n",
        language="python",
        policy=GradingPolicy(
            agent_timeout_sec=3600.0,
            verifier_timeout_sec=900.0,
            image_ref="img:1",
            workspace_excludes=[".git"],
        ),
    )
    scripts = []
    for step in steps:
        scripts += [step.test_script, step.aux_files["workdir/setup.sh"]]
        if step.solve_script:
            scripts.append(step.solve_script)
    assert scripts
    for script in scripts:
        result = subprocess.run(["bash", "-n"], input=script, capture_output=True, text=True)
        assert result.returncode == 0, f"generated shell failed bash -n: {result.stderr}"


def test_instruction_references_no_task_supplied_command() -> None:
    """The instruction may not advertise a CLI the image does not install.

    Regression gate for the deleted `chain` controller: backticked tokens must
    be data (paths, repo slug, commit prefix, subsystem), never a command.
    """
    import re

    chain = _chain_of(3)
    text = build_chain_instruction(chain, repo="o/n", stage_count=3)
    assert "```bash" not in text
    for token in re.findall(r"`([^`]+)`", text):
        first = token.split()[0]
        is_data = "/" in first or re.fullmatch(r"[0-9a-f]{2,40}", first) or first == chain.subsystem
        assert is_data, f"backticked token looks like a command: {token!r}"


# ---------------------------------------------------------------------------
# stage validation cache
# ---------------------------------------------------------------------------


def test_validation_cache_makes_revalidation_free(tmp_path) -> None:
    """Second pass over the same chain must run zero tests.

    The cache is what makes interrupted batches and multi-worker runs cheap;
    a regression here is a silent 4x test-run cost per stage.
    """
    from repo2rlenv.bootstrap.docker import ExecResult
    from repo2rlenv.pipelines._pr_chain_validate import StageValidationCache, validate_chain

    chain = _chain_of(1)

    class FakeSandbox:
        def __init__(self):
            self.test_runs = 0

        def exec(self, command: str, *, timeout: int = 300) -> ExecResult:
            if "echo OK" in command:  # git presence + commit presence probes
                return ExecResult(0, "OK", "", 0.1)
            if "git reset --hard" in command:
                self.test_runs += 1
                # gold/head pass; base/start fail -> one clean F2P oracle
                if f"git reset --hard {chain.base_commit}" in command or " b1" in command:
                    body = "tests/test_1.py::test_fix FAILED\ntests/test_1.py::test_keep PASSED\n"
                else:
                    body = "tests/test_1.py::test_fix PASSED\ntests/test_1.py::test_keep PASSED\n"
                log = f"R2E_START_TEST_OUTPUT\n{body}R2E_END_TEST_OUTPUT\n"
                return ExecResult(1 if "FAILED" in body else 0, log, "", 1.0)
            return ExecResult(0, "", "", 0.1)

    cache = StageValidationCache(tmp_path / "cache.sqlite")
    first = validate_chain(
        sandbox=FakeSandbox(),
        chain=chain,
        base_test_cmds=["pytest -v"],
        min_stages=1,
        min_pass_to_pass=0,
        cache=cache,
    )
    assert first.status == "verified"
    assert first.verified_stages[0].fail_to_pass == ["tests/test_1.py::test_fix"]

    counting = FakeSandbox()
    second = validate_chain(
        sandbox=counting,
        chain=chain,
        base_test_cmds=["pytest -v"],
        min_stages=1,
        min_pass_to_pass=0,
        cache=cache,
    )
    assert counting.test_runs == 0  # all served from cache
    assert second.verified_stages[0].fail_to_pass == ["tests/test_1.py::test_fix"]
    cache.close()


def test_validation_cache_key_covers_the_oracle_inputs(tmp_path) -> None:
    """A change in any oracle input must miss the cache."""
    from repo2rlenv.pipelines._pr_chain_validate import StageValidationCache

    chain = _chain_of(1)
    cache = StageValidationCache(tmp_path / "c.sqlite")
    base_key = cache.key(
        chain, chain.stages[0], ["pytest -v"], "python", max_pass_to_pass=50, min_pass_to_pass=0
    )
    same = cache.key(
        chain, chain.stages[0], ["pytest -v"], "python", max_pass_to_pass=50, min_pass_to_pass=0
    )
    assert base_key == same
    other_cmd = cache.key(
        chain, chain.stages[0], ["pytest -x"], "python", max_pass_to_pass=50, min_pass_to_pass=0
    )
    assert other_cmd != base_key
    cache.close()


def test_shell_templates_are_shellcheck_clean() -> None:
    """Templates are the only generated shell; keep them lint-clean in CI too."""
    import shutil
    import subprocess

    shellcheck = shutil.which("shellcheck")
    if shellcheck is None:
        pytest.skip("shellcheck not installed")
    # Render through the real builders: raw templates contain placeholders.
    scripts = [
        build_step_setup_script(has_carry=True),
        build_step_setup_script(has_carry=False),
        build_step_solve_script(),
        build_step_test_script(test_cmds=["pytest -v -n 0 tests/t.py"], language="python"),
        build_step_test_script(test_cmds=[], language=None),
    ]
    result = subprocess.run(
        [shellcheck, "--severity=warning", "--shell=bash", "-"],
        input="\n# --- next script ---\n".join(scripts),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
