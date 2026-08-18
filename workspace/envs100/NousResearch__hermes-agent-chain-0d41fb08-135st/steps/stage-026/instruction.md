**fix(slack): handle assistant thread lifecycle events**

## Summary

Salvages PR #6280 by @helix4u onto current main.

Adds handling for Slack's AI Assistant lifecycle events (`assistant_thread_started` and `assistant_thread_context_changed`). When Slack is in AI Assistant mode, these events arrive before/alongside regular message events and carry the user identity + thread metadata that assistant-thread DMs can be missing. Without this, assistant threads lose user identity, breaking session tracking and memory scoping.

**Changes:**
- Register `assistant_thread_started` and `assistant_thread_context_changed` event handlers
- Cache assistant-thread metadata (channel_id, thread_ts, user_id, team_id) for identity recovery
- Seed session store from lifecycle events so per-user session scoping is initialized early
- Modify `_handle_slack_message()` to consult cached identity when message events are missing user info
- Infer `channel_type="im"` from `D`-prefix channels when missing
- **Follow-up fix:** Add `_ASSISTANT_THREADS_MAX` (5000) size cap with LRU eviction to prevent unbounded cache growth

## Test results
```
72 passed, 16 warnings in 0.22s
```

Co-authored-by: helix4u <4317663+helix4u@users.noreply.github.com>