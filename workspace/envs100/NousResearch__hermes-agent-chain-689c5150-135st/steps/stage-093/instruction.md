**fix: strip reasoning item IDs from Responses API input when store=False**

## Summary

Fixes a 404 error when using GPT-5.x models on the Responses API. With `store=False` (our default), reasoning items from previous turns were replayed with their `id` fields, causing the API to attempt a server-side lookup that fails since nothing was persisted.

**Error:**
```
Item with id 'rs_01a228e5...' not found. Items are not persisted when store is set to false.
```

**Root cause:** `_chat_messages_to_responses_input` and `_preflight_codex_input_items` both included the `id` field on reasoning items sent back to the API. The `encrypted_content` blob is self-contained for reasoning chain continuity — the `id` triggers an unnecessary (and failing) server-side lookup.

**Fix:** Strip `id` from reasoning items in both conversion layers. The id is still used for local deduplication (preventing duplicate reasoning items across turns) but never sent to the API.

## Changes
- `run_agent.py`: Strip `id` from reasoning items in `_chat_messages_to_responses_input` and `_preflight_codex_input_items`
- `tests/run_agent/test_run_agent_codex_responses.py`: Update dedup tests to verify IDs are stripped