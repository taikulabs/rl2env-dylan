**fix: preserve session_id across previous_response_id chains in /v1/responses**

## Summary

Fixes a bug where every `/v1/responses` request created a new session on the web dashboard, even when `previous_response_id` was passed for multi-turn conversation chaining.

**Root cause:** Line 1485 in `api_server.py` unconditionally generated `session_id = str(uuid.uuid4())` for every request. The `ResponseStore` correctly chained conversation history but never stored or restored the `session_id`, so each turn got its own session entry in `SessionDB`.

**Fix:**
- Store `session_id` alongside the response in `ResponseStore.put()` (both streaming and non-streaming paths)
- When `previous_response_id` resolves, extract and reuse the stored `session_id`
- Applies to `/v1/responses` (streaming + non-streaming) and `/v1/runs` endpoints
- Explicit `body.session_id` on `/v1/runs` still takes priority over stored session