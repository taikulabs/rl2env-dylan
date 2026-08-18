"""Typed plan for a chain task: one `StagePlan` per native Harbor step.

The plan is the contract between validation, step rendering, and the emitted
`chain/plan.json`. Typing it (instead of `dict[str, object]`) removes the
`assert isinstance` checks and `str(entry[...])` casts the dict forced on every
consumer — and makes a missing field a construction error rather than a
KeyError at emission time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class StagePlan:
    """One graded milestone: a native Harbor step's worth of work."""

    index: int
    pr_number: int | None
    title: str
    instruction: str
    # The tree the agent starts from (previous kept stage's gold, so dropped
    # stages leave no hole in the replay).
    before_commit: str
    # The commit this stage's own diff starts from; before→carry is the free
    # churn applied at step setup.
    carry_commit: str
    # This stage's gold tree.
    after_commit: str
    source_paths: list[str] = field(default_factory=list)
    test_paths: list[str] = field(default_factory=list)
    test_cmds: list[str] = field(default_factory=list)
    fail_to_pass: list[str] = field(default_factory=list)
    pass_to_pass: list[str] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "pr_number": self.pr_number,
            "title": self.title,
            "instruction": self.instruction,
            "before_commit": self.before_commit,
            "carry_commit": self.carry_commit,
            "after_commit": self.after_commit,
            "source_paths": self.source_paths,
            "test_paths": self.test_paths,
            "test_cmds": self.test_cmds,
            "fail_to_pass": self.fail_to_pass,
            "pass_to_pass": self.pass_to_pass,
        }


@dataclass(frozen=True, slots=True)
class ChainPlan:
    """A validated chain rendered as a sequence of stages."""

    repo: str
    base_commit: str
    head_commit: str
    subsystem: str
    coherence: float
    stages: list[StagePlan] = field(default_factory=list)

    @property
    def pr_numbers(self) -> list[int]:
        # TOML has no null: only stages with a resolved PR are listed. The
        # stage count is the authoritative total.
        return [s.pr_number for s in self.stages if s.pr_number is not None]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "base_commit": self.base_commit,
            "head_commit": self.head_commit,
            "subsystem": self.subsystem,
            "coherence": self.coherence,
            "pr_numbers": self.pr_numbers,
            "stages": [s.to_json_dict() for s in self.stages],
        }
