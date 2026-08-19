**fix(gateway): route watch-pattern notifications to originating session**

## Summary

Salvage of #10446 by @kshitijk4poor (itself a salvage of #9537 by @etcircle). Fixes background process watch-pattern notifications leaking into whichever Discord/Telegram thread is active when the queue drains, instead of routing back to the thread that originally started the process.

### Root cause

`_inject_watch_notification(synth_text, event)` in gateway/run.py passed the **current foreground event** (whatever thread the user just messaged from) instead of the process's own routing metadata. Additionally, `terminal_tool.py` only populated watcher routing fields when `notify_on_complete` was set — watch-pattern-only processes had empty routing metadata.

### Changes (from #9537 + #10446)

1. **process_registry.py** — Watch event dicts now carry `session_key` + routing fields (`platform`, `chat_id`, `thread_id`, etc.)
2. **gateway/run.py** — New `_build_process_event_source(evt)` resolves the correct `SessionSource` via 3-tier fallback: session store → session key parse → event dict fields
3. `_inject_watch_notification()` takes the queue event dict instead of the foreground event
4. `_run_process_watcher` completion path also uses `_build_process_event_source`
5. **terminal_tool.py** — Routing metadata populated for `notify_on_complete OR watch_patterns` (was only `notify_on_complete`)
6. **`_parse_session_key()` helper** — Extracted duplicated session key parsing, used by shutdown notifications and process event routing

### Follow-up fixes (our commit)

| Fix | Description |
|-----|-------------|
| **`_parse_session_key` includes thread_id** | The helper now extracts the optional 6th part (thread_id) so shutdown notifications route to the correct forum topic |
| **Stale `parts` reference fixed** | `_notify_active_sessions_of_shutdown` referenced the removed `parts` variable — NameError was silently caught by try/except, breaking all shutdown notifications |
| **Updated tests** | `_parse_session_key` tests updated to verify thread_id extraction; added user_id-part test |

### Test results

- 94 passed (all PR-specific + restart_drain tests), 0 failures

Based on #9537 by @etcircle and #10446 by @kshitijk4poor. .