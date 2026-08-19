**fix(acp): mark failed tool completions in Zed**

Salvage of #26573 by @HenkDz cherry-picked onto current main, plus a follow-up commit extending the rule to cover raised exceptions.

## Summary
Before this PR, every tool call rendered as a green 'completed' row in Zed regardless of whether it succeeded — `build_tool_complete` unconditionally sent `status='completed'`. Now failures are surfaced as red 'failed' rows.

## Changes
### From #26573 (HenkDz, preserved authorship)
- `acp_adapter/tools.py`: new `_tool_result_failed()` helper that flags structured JSON results with `success:false` / `ok:false` / non-zero `exit_code` / non-zero `returncode`, plus `{error:...}` payloads from polished tools. Wired into `build_tool_complete`'s status field.
- `tests/acp/test_tools.py`: 7 tests covering each positive case + negative cases (plain 'tests failed' text stays completed, polished-only gate on bare {error:...}).

### Extension (this salvage)
- Also flags results starting with `"Error executing tool '"` — the unique prefix the agent's tool executor wraps around raised exceptions (`agent/tool_executor.py`). Without this, raised exceptions still rendered green. 2 new tests (positive: raised-exception prefix → failed; negative: bare `Error:` word in legit output stays completed).

## Validation
`scripts/run_tests.sh tests/acp/test_tools.py` → 70/70 passing.

 (salvage merge — HenkDz's commits preserved verbatim, extension as separate commit).