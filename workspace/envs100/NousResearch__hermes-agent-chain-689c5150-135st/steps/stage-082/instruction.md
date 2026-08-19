**feat: auto-continue interrupted agent work after gateway restart**

## Summary

 — when the gateway restarts mid-agent-work, the user no longer has to manually type "continue" or use `/retry`. The agent automatically picks up where it left off.

### The problem

When the gateway dies while the agent is mid-tool-loop, the session transcript ends on a `tool` message (the tool result the agent never processed). On the next user message:

1. History is loaded: `...assistant(tool_calls) → tool(result)`
2. User's new message is appended
3. The model sees `tool → user` and treats it as a new conversation turn
4. The interrupted work is silently abandoned

### The fix

**gateway/run.py** (+15 lines): In `_run_agent()`'s `run_sync` closure, after building `agent_history` and before calling `run_conversation()`, check if the last message is `role='tool'`. If so, prepend a system note:

```
[System note: Your previous turn was interrupted before you could process
the last tool result(s). Please finish processing those results and
summarize what was accomplished, then address the user's new message below.]
```

The model sees the full history (including pending tool results) + the note + the user's message. It finishes the interrupted work, summarizes what happened, then addresses the new input.

### Design decisions

- **No new session flags or schema changes** — purely detects trailing tool messages in loaded history
- **Works for all restart scenarios** (clean, crash, SIGTERM, drain timeout) as long as the session wasn't suspended
- **Suspended sessions get a fresh start** — no false auto-continue on nuked history
- **User's actual message is preserved** after the note
- **Also updates shutdown notification**: "Use /retry" → "Send any message after restart to resume" (now accurate)