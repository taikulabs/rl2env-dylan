**fix: send busy-session ack when user messages during active agent run**

## Summary

When a user sends a message while the agent is executing a task on the gateway, they previously got **complete silence** — the message was silently queued and only processed after the task finished (potentially 1+ hours later).

Reported by [@Lonely__MH](https://x.com/Lonely__MH/status/2044077241827823669):
> *'Hermes is executing a task, and if you ask it another question, it won't respond at all — what do you do?'*

### Root cause

The two-level message guard system had a gap:
- **Level 1** (base.py) caught ALL messages for active sessions, stored them in `_pending_messages`, set an asyncio.Event, and returned — **no response to user**
- **Level 2** (gateway/run.py) which calls `agent.interrupt()` was **never reached** because Level 1 already intercepted the message
- The interrupt mechanism was disconnected: the asyncio.Event didn't trigger `agent.interrupt()`, so the agent didn't even know about the user's message

### Fix

Expand `_handle_active_session_busy_message()` to handle the normal (non-draining) case:

1. **Queue the message** via `merge_pending_message_event` (processed after task finishes)
2. **Call `running_agent.interrupt(text)`** to signal the agent to wrap up sooner
3. **Send a status-rich acknowledgment** with iteration count, elapsed time, and current tool
4. **Debounce** acks to once per 30s per session to avoid spamming rapid messages

User now sees:
> ⏳ Still working on the current task (10 min elapsed, iteration 21/60, running: terminal). Your message has been queued and will be processed next. Use /stop to interrupt.