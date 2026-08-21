**fix(cron): deliver final report on last allowed turn instead of failing**

## Summary
Cron jobs that produce a complete final report no longer fail with a RuntimeError whose text *is* the report.

Two adjacent completion-boundary bugs that share the same user symptom ("cron ran, final message was created, but failed with a runtime error"):

1. A normal final text response landing on the **last allowed** API call was marked `completed=False` (`api_call_count == max_iterations`), so `cron/scheduler.py` raised the response as an error.
2. When the budget was genuinely exhausted but the toolless summary produced a usable report (`max_iterations_reached(...)` + non-empty `final_response`), cron still raised instead of delivering it.

Root cause confirmed against current `main`:
- `agent/conversation_loop.py` increments `api_call_count` to exactly `max_iterations` on the last pass, then captures the final text.
- `agent/turn_finalizer.py`: `completed = ... and api_call_count < agent.max_iterations` → False despite a complete answer.
- `cron/scheduler.py`: `if completed is False: raise RuntimeError(final_response)`.

## Changes
- `agent/turn_finalizer.py`: `completed=True` when the turn exited via `text_response(...)`, regardless of whether it used the last call. Genuine budget-exhaustion (`final_response is None`) stays incomplete.
- `cron/scheduler.py`: deliver a non-empty `max_iterations_reached(...)` summary instead of raising; log a warning.

## Validation
| | Before | After |
|---|---|---|
| Final text on last allowed call | `completed=False` → RuntimeError(report) | `completed=True` → delivered |
| Budget-exhausted summary (non-empty) | RuntimeError(summary) | delivered + warning logged |
| Genuine empty exhaustion | incomplete (raise) | incomplete (raise) — unchanged |

`tests/agent/test_turn_finalizer_cleanup_guard.py` + `tests/cron/test_scheduler.py` → 169 passed.

Salvage of #50967 by @helix4u (both commits 

## Infographic

![cron-deliver-final-report](https://v3b.fal.media/files/b/0a9f5aa1/1c9dDg7AWrDILif1hKYzy_DGYfsO0H.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`