**feat(cron): add wakeAgent gate — scripts can skip the agent entirely**

## Summary

Cron pre-check scripts can now skip the agent run entirely by writing `{"wakeAgent": false}` as their last stdout line. Useful for frequent polls (every 1-5 min) that only need to wake the LLM when something has genuinely changed.

## Changes

- `cron/scheduler.py`:
  - New pure helper `_parse_wake_gate(script_output)` — parses the last non-empty stdout line as JSON, returns `False` only on strict `{"wakeAgent": false}`, `True` for everything else (non-JSON, non-dict, missing key, truthy/falsy non-False values)
  - `_build_job_prompt(job, prerun_script=None)` — new optional `prerun_script` arg lets `run_job` pass pre-executed script output so the script runs exactly once per cron tick
  - `run_job` short-circuits with `SILENT_MARKER` (no LLM call, no delivery) when the gate fires
- `tests/cron/test_scheduler.py`:
  - `TestParseWakeGate` — 11 pure unit tests (empty, whitespace, non-JSON, non-dict, missing key, truthy/falsy non-False, multi-line, trailing blanks, non-last-line JSON)
  - `TestRunJobWakeGate` — 5 integration tests (skip returns SILENT + agent not invoked, wake-true runs agent with injected output, script runs only once, script failure doesn't trigger gate, no-script regression path)

## Why this instead of PR #3837

PR #3837 proposed the same idea but replaced main's sandboxed Python-script model with inline bash execution via tempfile. That design:
- Lost path-traversal protection + scripts-dir sandbox that main has
- Ran arbitrary bash (wider attack surface)
- Lost secret redaction on script stdout

This PR keeps main's sandboxed `_run_job_script()` as-is (Python scripts in `HERMES_HOME/scripts/` with path guards + secret redaction) and just adds the ~15-line `_parse_wake_gate` check on top.

Credit to the nanoclaw #1232 port effort — the wake/skip idea is useful, just porting it onto the stronger existing base.

## Validation

| | Before | After |
|---|---|---|
| Cron job with pre-check script returning `{wakeAgent: false}` | Agent always ran, tokens burned | Agent skipped, SILENT delivery suppression |
| Cron job with script returning `{wakeAgent: true, data: ...}` | Full stdout injected, agent runs | Same — backward compatible |
| Cron job with plain-text script output | Injected as context, agent runs | Same — non-JSON last line wakes |
| Cron job with malformed JSON / non-dict / missing `wakeAgent` | Injected as context, agent runs | Same — safe defaults wake the agent |
| Cron job with script `{wakeAgent: 0}` (truthy/falsy shortcut) | N/A | Still wakes — only strict `False` skips |
| Cron job without script | Unchanged | Unchanged (regression test) |
| Script run count per cron tick | 1 (when gate absent) | 1 (unchanged — `prerun_script` arg avoids re-execution) |

Tests: 16 new targeted tests pass; full `tests/cron/` suite 194/194 pass.

Closes follow-up request from #3837 closure.