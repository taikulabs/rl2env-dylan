**fix(kanban): restrict goal_mode kanban_block to genuine external blockers**

## Summary
Closes the second, ungated exit out of the `goal_mode` loop. `kanban_complete` got an auxiliary-judge gate, but `kanban_block` — which the goal loop treats as terminal identically to `done` — was left wide open, letting a worker that learns the complete path is gated escape with `kanban_block(reason="anything")` and zero judge involvement. This is Issue #38696.

## Changes
- `tools/kanban_tools.py`: `_handle_block` now restricts `goal_mode` tasks to `kind ∈ {dependency, needs_input}` — the two kinds that represent a genuine external blocker the worker cannot resolve itself. `capability`, `transient`, and unset are rejected with a message directing the worker to `kanban_complete` (which the judge gates). Deterministic allowlist (the issue's "Option B"), no extra judge LLM call — block legitimacy is a clean taxonomic question, so there's no fail-open concern. Non-`goal_mode` tasks are completely unaffected.
- `tests/tools/test_kanban_tools.py`: 5 new tests covering reject-missing-kind, reject-disallowed-kind, allow-dependency, allow-needs_input, and non-goal-mode-unaffected.

## Validation
| Case | Result |
|---|---|
| goal_mode + no kind | rejected, stays `running` |
| goal_mode + capability / transient | rejected, stays `running` |
| goal_mode + dependency | allowed → `todo` |
| goal_mode + needs_input | allowed → `blocked` |
| non-goal_mode + no kind | blocks freely → `blocked` (unchanged) |
| invalid kind | still hits kind-validation before the goal gate |

`scripts/run_tests.sh tests/tools/test_kanban_tools.py` → 97 passed, 0 failed. E2E verified against a real kanban DB in an isolated `HERMES_HOME`.

Salvaged from #55861 by @srojk34 (İsco); cherry-picked onto current main with authorship preserved.

## Infographic
![infographic](https://v3b.fal.media/files/b/0aa06a9f/2lWgPE5JkfdnCCJFyCVMK_pmSmz6Pz.png)