**fix(gateway): suppress duplicate replies on interrupt and streaming flood control**

## Summary

Fixes the duplicate reply bug reported by Discord user Farzad and tracked across three issues. The fix is platform-agnostic — all gateway platforms (Discord, Telegram, Slack, WhatsApp, etc.) benefit.

**What this PR does:** Prevents the gateway from sending the same response twice when:
- A new message arrives while the agent is still processing (interrupt race)
- Streaming delivers content but flood control prevents the final edit, causing the full response to be re-sent as a separate message

## Root Cause

Two independent mechanisms caused duplicate replies:

### 1. Stale response on interrupt (#8221, #2483)
In `base.py`, after `_message_handler()` returns, the response was always sent — even when the session had been interrupted by a new message. The user would see the stale answer to their old question, followed by the answer to their new one.

**Fix:** Check `interrupt_event.is_set()` AND `session_key in self._pending_messages` before sending. Both conditions must hold to avoid false positives (photo bursts don't set the interrupt event).

### 2. Streaming already_sent flag race
In `run.py`, the `already_sent` flag required BOTH `response_previewed` (agent-level) AND `already_sent` (stream consumer delivery-level). When flood control interrupted the final streaming edit:
- `already_sent=True` (content was delivered via streaming)
- `response_previewed=False` (not set in this code path)
- Combined: `False` → duplicate send not suppressed

**Fix:** Remove the `response_previewed` guard. The stream consumer's `already_sent` is the authoritative delivery signal — if content reached the user via streaming, suppress the duplicate regardless of the agent's internal preview state.

## Changes

| File | Change | Lines |
|------|--------|-------|
| `gateway/platforms/base.py` | Suppress stale response when interrupted | +15 |
| `gateway/run.py` (return path) | Remove response_previewed guard | -5, +1 |
| `gateway/run.py` (queued-message path) | Remove response_previewed guard | -5, +1 |
| `tests/gateway/test_duplicate_reply_suppression.py` | 10 new tests covering all fix paths | +290 |