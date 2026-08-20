**fix(agent): restrict background review fork to memory + skills toolsets**

## Summary
Background memory/skill review fork can no longer run terminal, send_message, delegate_task, browser, web, or file tools. Restricted to `memory` + `skills` only — which is everything the review prompts actually need.

.

## Changes
- `run_agent.py`: one-line `enabled_toolsets=["memory", "skills"]` added to the `AIAgent(...)` construction in `_spawn_background_review()`.
- `tests/run_agent/test_background_review_toolset_restriction.py`: regression coverage.

## Validation
Targeted test suite: 2/2 passed.

## Credit
Salvage of #16001 by @luyao618 onto current main (251 commits ahead of the original branch). Cherry-picked with original authorship preserved.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_background_review_toolset_restriction.py`