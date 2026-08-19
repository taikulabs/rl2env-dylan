**fix(acp): replay assistant reasoning as agent_thought_chunk on session/load**

## Summary

Replays persisted assistant `reasoning_content` / `reasoning` fields as ACP `agent_thought_chunk` notifications during `session/load` and `session/resume`, so editor clients (Zed, etc.) reconstruct collapsed Thinking panes when re-opening a session that used a thinking model — instead of restoring everything except the thoughts.

.

## Background

When `session/load` was first implemented, replay covered nothing (#12285 original report). Subsequent merges substantially closed the gap:

- **#17874** (salvage of @HenkDz's #17652) — initial `_replay_session_history` for user/assistant text chunks.
- **#19139** (salvage of @HenkDz's #18578) — added tool-call `start`/`complete` replay, post-response scheduling, usage updates, ~35 polished tool renderers.
- **#26583** (salvage of #26393) — native `plan` rebuilding from persisted `todo` results.
- **#16892** — write-side normalization so streamed `reasoning_text` lands in `reasoning_content` on disk reliably across providers (the prerequisite that makes thought replay actually meaningful for non-DeepSeek thinking models).

The one piece still missing was thought replay itself: persisted `reasoning_content` / `reasoning` fields were silently dropped during replay, even though they're emitted as `agent_thought_chunk` live via `acp.update_agent_thought_text` in `events.py::make_thinking_cb`.

This PR adds that last piece. It's the gap @Yukipukii1's #14691 originally aimed at; their PR predates #19139's tool replay so it would conflict heavily on rebase, but the contribution is credited (#14691 introduced the design for thought replay alongside `update_user_message_text` / `update_agent_message_text` mappings).

## Changes

### `acp_adapter/server.py`

- New `_flatten_history_text(value)` shared between `_history_message_text` and the new `_history_reasoning_text` — both shapes (scalar string / list of `{text, ...}` parts) handled in one place.
- New `_history_reasoning_text(message)` prefers `reasoning_content` (canonical ) and falls back to `reasoning` (legacy / SDK-attr path).
- New `_history_thought_update(text)` peers `_history_message_update` so all replay-chunk construction goes through the same factory layer.
- `_replay_session_history` reshape: the `assistant` branch now handles thought → message text → tool_calls in one block, matching how live streaming orders them (`reasoning_callback` deltas precede `stream_delta_callback`). The `user` branch is split out for clarity; behavior on non-reasoning histories is unchanged.

### `tests/acp/test_server.py`

Three new tests:
- `test_load_session_replays_reasoning_thought_before_message` — both `reasoning_content` and legacy `reasoning` paths fire; thought precedes message in the same turn.
- `test_load_session_replays_reasoning_only_turn` — reasoning-only assistant entries (empty `content`) still surface a thought.
- `test_load_session_skips_empty_reasoning_fields` — whitespace-only reasoning doesn't emit a spurious chunk.

## Validation

- `bash scripts/run_tests.sh tests/acp/ --ignore=tests/acp/test_registry_manifest.py` — **236 passed** (the two `test_registry_manifest.py` failures are a pre-existing v0.13.0/v0.14.0 fixture mismatch on `origin/main`, unrelated).
- `ruff check acp_adapter/server.py tests/acp/test_server.py` — clean.
- **Behavior parity** check against `origin/main` for histories without reasoning fields: identical notification stream (`user_message_chunk | agent_message_chunk | user_message_chunk | tool_call | tool_call_update`). Pure additive change.
- **E2E** against an isolated `HermesACPAgent` exercising the real `_replay_session_history`: confirms thought emitted before message text, both `reasoning_content` and `reasoning` paths fire, reasoning-only turns emit only thought, whitespace-only reasoning emits nothing, and the tricky case (assistant message with reasoning + tool_calls + empty content) produces `thought → tool_call → tool_call_update` with no spurious empty message chunk.

## Credit

-

…(truncated)