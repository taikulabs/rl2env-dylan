**fix(agent): handle concurrent tool submit shutdown**

## Summary
Concurrent tool batches no longer crash the conversation loop when Python is shutting down the interpreter mid-batch.

`ThreadPoolExecutor.submit()` can raise `RuntimeError: cannot schedule new futures after interpreter shutdown`. In `_execute_tool_calls_concurrent()` the submit loop was unguarded, so that error escaped the function and took down the outer agent loop (reported on v0.17.0, macOS/TUI, opencode-go/deepseek-v4-pro, large response at ~91s).

The fix catches only that specific submit-time error: it records ordered failed tool-results for the not-yet-submitted calls and breaks the loop, letting already-submitted futures finish through the existing wait + post-processing path.

## Changes
- `agent/tool_executor.py`: wrap `executor.submit()`; on the interpreter-shutdown `RuntimeError`, mark the unsubmitted tail (`runnable_calls[submit_index:]`) as ordered failed results and stop scheduling. Non-matching `RuntimeError`s re-raise unchanged.
- `tests/run_agent/test_run_agent.py`: regression test — `submit()` raising the shutdown error yields ordered tool-result messages instead of escaping.

## Validation
| Check | Result |
|---|---|
| Bug reproduced on main | yes — unwrapped `executor.submit()` |
| Targeted concurrent tests | 35 passed |
| E2E (real AIAgent, real path, mid-batch submit failure) | no escape; 3 ordered msgs; submitted tool returns real result; unsubmitted tail carries shutdown error |
| ruff | clean |

E2E exercised the genuine path: a real `AIAgent._execute_tool_calls_concurrent` with a real `ThreadPoolExecutor` whose 2nd `submit()` raises the actual shutdown `RuntimeError` mid-batch — the in-flight future completed with its real result while the unsubmitted calls became ordered failed results, and nothing propagated out of the function.

Salvage of #51537 — cherry-picked to preserve @helix4u's authorship.