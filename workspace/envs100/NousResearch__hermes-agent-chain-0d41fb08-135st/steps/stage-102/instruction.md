**feat: Background Process Monitoring — watch_patterns for real-time output alerts**

## Background Process Monitoring

Hermes agents can now **monitor background processes in real-time** and react to specific output the moment it appears — no polling, no wasted tokens, no manual checking.

```python
terminal(
    command='npm run dev',
    background=true,
    watch_patterns=['ERROR', 'WARN', 'listening on port']
)
```

The agent keeps working on other tasks. The instant `ERROR` appears in the process output, Hermes wakes up and reacts — fixes the bug, restarts the server, notifies the user. Zero-cost while the output is clean.

This turns background processes from fire-and-forget into **event-driven workflows**: start a dev server and get alerted on crashes. Run a test suite and react to the first failure while the rest still runs. Deploy to production and watch for errors in real time. Monitor build output for warnings before they become blockers.

## How It Works

One new parameter on the existing `terminal` tool — no new tools, no schema bloat. The agent passes a list of strings to watch for, and Hermes handles the rest:

- **Pattern matching** runs inside the existing reader threads across all backends (local, Docker, SSH, Modal, Daytona, Singularity)
- **Notifications** flow through the unified `completion_queue` alongside `notify_on_complete` events — same proven delivery path, same consumption points in CLI and gateway
- **Rate limiting** prevents noisy processes from burning tokens: 8 notifications per 10-second window, with a 45-second sustained-overload kill switch
- **Crash recovery** persists watch patterns in the checkpoint file so gateway restarts don't lose monitoring state

Stacks with `notify_on_complete` — use both to get pattern alerts while running AND a completion summary when done.

## What the Agent Sees

When a pattern matches:
```
[SYSTEM: Background process proc_abc123 matched watch pattern "ERROR".
Command: npm run dev
Matched output:
TypeError: Cannot read property 'foo' of undefined
    at Server.handler (app.js:42:15)]
```

If rate-limited:
```
[SYSTEM: Background process proc_abc123 matched watch pattern "ERROR".
Command: npm run dev  
Matched output:
Error: connection refused
(12 earlier matches were suppressed by rate limit)]
```

## Changes

| File | What |
|------|------|
| `tools/process_registry.py` | `ProcessSession.watch_patterns`, rate-limit state, `_check_watch_patterns()` in all 3 reader threads, unified queue with `type` field, checkpoint persistence |
| `tools/terminal_tool.py` | `watch_patterns` array parameter in schema + handler |
| `cli.py` | `_format_process_notification()` — unified formatter for completions + watch events, drain at both idle and post-turn sites |
| `gateway/run.py` | `_format_gateway_process_notification()`, `_inject_watch_notification()`, post-agent-run drain |
| `tools/code_execution_tool.py` | `watch_patterns` blocked in execute_code sandbox |
| `tests/tools/test_watch_patterns.py` | 20 tests covering matching, rate limiting, overload kill, checkpoint persistence, schema, handler |

## E2E Verified

Interactive CLI session: started a 30-iteration loop printing ERROR every 5th line. Agent received the watch notification while idle, woke up, reported all 6 ERROR lines. Full pipeline confirmed working across pattern matching → queue → idle drain → synthetic message injection → agent turn.

## Tests

```
20 passed — test_watch_patterns.py
59 passed — test_notify_on_complete.py + test_process_registry.py (no regressions)
7 passed  — test_terminal_tool.py (no regressions)
```