"""Tests for pr_arc: TB-style standalone tasks derived from real PRs."""

from __future__ import annotations

import json
from pathlib import Path

from repo2rlenv.pipelines.pr_arc import (
    Arc,
    ArcStage,
    build_arc_instruction,
    build_arc_task,
    load_arc_stages,
    select_arcs,
    select_singletons,
    task_slug,
    validate_arc,
)


def _stage(index: int, **kwargs) -> ArcStage:
    base = {
        "index": index,
        "pr_number": 100 + index,
        "title": f"fix: thing {index}",
        "instruction": f"Fix thing {index}: the fuller problem statement for {index}.",
        "before_commit": f"b{index}",
        "after_commit": f"a{index}",
        "test_paths": [f"tests/test_{index}.py"],
        "fail_to_pass": [f"tests/test_{index}.py::test_fix"],
        "pass_to_pass": [f"tests/test_{index}.py::test_keep"],
        "source_paths": [f"src/thing_{index}.py"],
    }
    base.update(kwargs)
    return ArcStage(**base)


def test_load_arc_stages_round_trips_a_plan(tmp_path: Path) -> None:
    plan = {
        "stages": [
            {
                "index": 1,
                "pr_number": 101,
                "title": "fix: a",
                "instruction": "Fix a.",
                "before_commit": "b1",
                "carry_commit": "b1",
                "after_commit": "a1",
                "source_paths": ["src/a.py"],
                "test_paths": ["tests/test_a.py"],
                "test_cmds": ["pytest -v tests/test_a.py"],
                "fail_to_pass": ["tests/test_a.py::test_fix"],
                "pass_to_pass": [],
            }
        ]
    }
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    (stage,) = load_arc_stages(path)
    assert stage.index == 1
    assert stage.fail_to_pass == ["tests/test_a.py::test_fix"]


def test_select_arcs_tiles_into_small_groups() -> None:
    stages = [_stage(i + 1) for i in range(12)]
    arcs = select_arcs(stages)
    assert [len(a.stages) for a in arcs] == [5, 5, 2]
    assert all(len(a.stages) <= 5 for a in arcs)


def test_select_singletons_picks_measured_hard_or_large() -> None:
    easy = _stage(1)
    big = _stage(2, source_paths=[f"src/f{n}.py" for n in range(4)])
    measured = _stage(3)
    stages = [easy, big, measured]
    singletons = select_singletons(stages, hard_indices={3})
    assert [a.stages[0].index for a in singletons] == [2, 3]


def test_task_slug_is_kebab_and_bounded() -> None:
    arc = Arc(stages=(_stage(1, title="fix(cli): keep drain dedup after poll"),), subsystem="x")
    slug = task_slug(arc)
    assert slug == slug.lower()
    assert "__" not in slug
    assert len(slug.split("-")) <= 3


def test_arc_instruction_lists_every_part_and_the_tests() -> None:
    stages = [_stage(1), _stage(2)]
    text = build_arc_instruction(Arc(stages=tuple(stages), subsystem="x"))
    assert "Part 1" in text and "Part 2" in text
    assert "`tests/test_1.py`" in text and "`tests/test_2.py`" in text


def test_arc_task_is_tb_conformant(monkeypatch, tmp_path: Path) -> None:
    import tomllib

    from repo2rlenv.emitter.harbor import write_harbor_task

    monkeypatch.setattr(
        "repo2rlenv.pipelines.pr_arc.file_at_commit",
        lambda clone_dir, commit, path: f"# {path} @ {commit}\n",
    )
    monkeypatch.setattr(
        "repo2rlenv.pipelines.pr_arc.range_diff",
        lambda clone_dir, before, after: f"diff {before}..{after}\n",
    )
    arc = Arc(stages=(_stage(1), _stage(2)), subsystem="x")
    task = build_arc_task(
        arc,
        clone_dir=tmp_path,
        bootstrap_image="img:1",
        language="python",
        verifier_source="# v\n",
        org="repo2rlenv",
    )
    out = write_harbor_task(task, tmp_path / "out")

    text = (out / "instruction.md").read_text()
    assert text.startswith("<!-- harbor-canary GUID ")
    meta = tomllib.loads((out / "task.toml").read_text())["metadata"]
    assert meta["category"] == "Software"
    for field in (
        "difficulty_explanation",
        "solution_explanation",
        "verification_explanation",
        "expert_time_estimate_hours",
        "subcategory",
        "tags",
    ):
        assert meta.get(field), field
    assert meta["repo2env"]["reward_mode"] == "binary_clean_command"

    # The verifier is binary + clean-gated + CTRF-backed + unprivileged.
    test_sh = (out / "tests" / "test.sh").read_text()
    assert "--binary" in test_sh
    assert "--require-clean-command" in test_sh
    assert "setpriv --reuid nobody" in test_sh
    assert "--ctrf" in test_sh

    # Trusted tests + spec copies + compose + purge manifest.
    assert (out / "tests" / "files" / "tests" / "test_2.py").exists()
    assert (out / "environment" / "spec-tests" / "tests" / "test_1.py").exists()
    assert (out / "environment" / "docker-compose.yaml").exists()
    assert (out / "tests" / "purge.manifest").exists()
    assert (out / "manifest.json").exists()
    # The oracle is the arc's whole diff.
    assert "diff" in (out / "solution" / "patch.diff").read_text()


def test_validate_arc_prunes_and_gates() -> None:
    from repo2rlenv.bootstrap.docker import ExecResult

    arc = Arc(stages=(_stage(1),), subsystem="x")

    class FakeSandbox:
        def exec(self, command: str, *, timeout: int = 300) -> ExecResult:
            if "echo OK" in command:
                return ExecResult(0, "OK", "", 0.1)
            if "git reset --hard" in command:
                if " b1" in command or "b1" in command.split("reset --hard ")[1][:2]:
                    body = "tests/test_1.py::test_fix FAILED\ntests/test_1.py::test_keep PASSED\n"
                    code = 1
                else:
                    body = "tests/test_1.py::test_fix PASSED\ntests/test_1.py::test_keep PASSED\n"
                    code = 0
                return ExecResult(
                    code, f"R2E_START_TEST_OUTPUT\n{body}R2E_END_TEST_OUTPUT\n", "", 1.0
                )
            return ExecResult(0, "", "", 0.1)

    validated = validate_arc(FakeSandbox(), arc, language="python")  # type: ignore[arg-type]
    assert validated is not None
    assert validated.fail_to_pass == ["tests/test_1.py::test_fix"]
    assert validated.pass_to_pass == ["tests/test_1.py::test_keep"]

    class DirtyFinal(FakeSandbox):
        def exec(self, command: str, *, timeout: int = 300) -> ExecResult:
            if (
                "git reset --hard" in command
                and " b1" not in command
                and "reset --hard b1" not in command
            ):
                body = "tests/test_1.py::test_fix PASSED\ntests/test_1.py::test_other FAILED\n"
                return ExecResult(1, f"R2E_START_TEST_OUTPUT\n{body}R2E_END_TEST_OUTPUT\n", "", 1.0)
            return super().exec(command, timeout=timeout)

    assert validate_arc(DirtyFinal(), arc, language="python") is None  # type: ignore[arg-type]
