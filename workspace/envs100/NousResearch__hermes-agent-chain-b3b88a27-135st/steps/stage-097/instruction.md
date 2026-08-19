**fix(gateway): salvage stale-output/typing interrupt handling**

## Summary
- salvages helix4u's gateway interrupt/typing-loop fix from #12388 onto current main
- preserves the original contributor commits and adds one current-main follow-up commit to address review findings
- fixes stale commentary/tool-progress/typing leakage after `/stop` or `/new`

## What this fixes
This PR hardens the gateway interrupt path so old runs cannot keep leaking output after they are invalidated:
- generation invalidation now drops stale results safely
- adapter typing keepalive listens to session interruption and stops at the source
- control interrupt messages are filtered so they are not recycled as follow-up user input

## Current-main follow-up fixes included
On top of the original PR, this salvage fixes the review findings:
- deferred post-delivery callbacks are now generation-aware end-to-end, so stale runs cannot clear callbacks registered by a fresher run for the same session
- callback ownership is bound to the active session event at run start and snapshotted inside base adapter processing, avoiding the shared-event mutation race
- proxy mode now receives `run_generation` and drops stale proxy streams/final results too
- stop/new interrupt cleanup is centralized into one helper instead of being duplicated across multiple branches
- internal control interrupt reason strings use shared constants
- removed the `return` from `BasePlatformAdapter._process_message_background()`'s `finally` block so cleanup no longer swallows cancellation/exception flow
- added focused regressions for generation forwarding, proxy stale suppression, and newer-callback preservation

## Files changed
- `gateway/platforms/base.py`
- `gateway/run.py`
- `tests/gateway/test_pending_event_none.py`
- `tests/gateway/test_run_progress_topics.py`
- `tests/gateway/test_session_race_guard.py`
- `tests/gateway/test_status_command.py`
- `tests/gateway/test_proxy_mode.py`

## Verification
Focused gateway suite:
- `scripts/run_tests.sh tests/gateway/test_base_topic_sessions.py tests/gateway/test_run_progress_topics.py tests/gateway/test_session_race_guard.py tests/gateway/test_pending_event_none.py tests/gateway/test_status_command.py tests/gateway/test_plan_command.py tests/gateway/test_proxy_mode.py -q`
- result: `81 passed`

Syntax/smoke:
- `py_compile gateway/run.py`
- `py_compile gateway/platforms/base.py`
- `py_compile tests/gateway/test_status_command.py`
- `py_compile tests/gateway/test_proxy_mode.py`

## Contributor credit
This PR