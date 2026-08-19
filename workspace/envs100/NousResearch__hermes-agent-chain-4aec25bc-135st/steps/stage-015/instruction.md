**fix(acp): replay session history before responding to session/load (#12285 follow-up)**

## Summary

Switches `_replay_session_history` from `loop.call_soon`-deferred (after the response) to `await`-inline (before the response) for both `session/load` and `session/resume`. Spec-compliant ACP clients now see the full transcript within the load request's lifetime, matching every other reference ACP agent.

Follows up #26943 (which added thought-chunk replay but kept the deferred scheduling intact). Together, both PRs are needed to fully  for spec-compliant clients.

## Why

The deferral was added on May 2 in ` with the rationale: _"Zed only attaches streamed transcript/tool updates once the load/resume response has completed."_

That rationale was incorrect:

| Server / spec | Behavior |
|---|---|
| [ACP spec — Loading Sessions](https://agentclientprotocol.com/protocol/session-setup#loading-sessions) | _"Stream the entire conversation history back to the client via notifications"_ — natural JSON-RPC reading: during the request, before responding |
| [Zed source (`zed-industries/zed/crates/agent_servers/src/acp.rs`)](https://github.com/zed-industries/zed/blob/main/crates/agent_servers/src/acp.rs) | _"Register the session before awaiting the RPC so that any `session/update` notifications that arrive during the call (e.g. history replay during `session/load`) can find the thread."_ |
| [agentao ACP server](https://github.com/jin-bo/agentao/blob/main/docs/ACP.md) | _"emits one notification per entry **before** responding to the load request"_ |
| Codex / Claude Code / OpenCode / Pi | All replay-before-respond (verified empirically by a community user testing the same client against all of them) |
| **Hermes (before this PR)** | Deferred via `loop.call_soon`, fires AFTER the response resolves |

A community user running `@agentclientprotocol/sdk` v0.21.1 reported that their custom ACP test client works correctly against Codex / Claude Code / OpenCode / Pi but receives **0 notifications** from Hermes because they read the notification count immediately after `await loadSession()` resolves — at which point Hermes hadn't fired any session_update yet.

## Changes

### `acp_adapter/server.py`
- Remove `_schedule_history_replay` helper.
- Both `load_session` and `resume_session` now `await self._replay_session_history(state)` before constructing the response.
- Wrap each awaited replay in `try/except Exception` that logs and continues. This preserves the prior contract that "a malformed message can't turn a successful load into a JSON-RPC error" — partial transcripts are acceptable, total load failure is not.
- The `_fenced_text` change in `acp_adapter/tools.py` from the same May 2 commit is **intentionally left intact** — it's an orthogonal, still-valid fix for Zed's pipe-as-table rendering of file content.

### `tests/acp/test_server.py`
- Replace `test_load_session_schedules_history_replay_after_response` (which encoded the now-incorrect post-response ordering) with two tests asserting `events == ["replay", "returned"]` for `load_session` and `resume_session`.
- Add two regression tests (`test_load_session_survives_replay_helper_exception`, `test_resume_session_survives_replay_helper_exception`) confirming that a replay helper raising still yields a successful `LoadSessionResponse` / `ResumeSessionResponse` rather than propagating the exception as a JSON-RPC error.

## Validation

- `bash scripts/run_tests.sh tests/acp/ --ignore=tests/acp/test_registry_manifest.py` — **240 passed** (was 238). The 2 `test_registry_manifest.py` failures are pre-existing on `origin/main` (release-day v0.13.0/v0.14.0 fixture mismatch, unrelated).
- `ruff check acp_adapter/server.py tests/acp/test_server.py` — clean.
- **Behavior verified end-to-end** against the reported client pattern:

  ```
  Before (origin/main): notifications received DURING load_session call: 0
  After (this PR):      notifications received DURING load_session call: 6
  Kinds: ['user_message_chunk', 'agent_thought_chunk', 'agent_message_chunk',
          'user_message_chu

…(truncated)