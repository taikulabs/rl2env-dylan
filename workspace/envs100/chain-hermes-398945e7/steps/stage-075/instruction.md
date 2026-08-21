**fix(gateway/slack): ephemeral slash-command ack, private notice delivery, format_message fixes**

## Summary

 and salvages #9340 — comprehensive Slack ephemeral messaging improvements:

1. **Slash commands now show ephemeral acknowledgements** (`/q`, `/btw`, `/stop`, `/model`, etc.) and route command replies ephemerally, matching Discord's behavior.
2. **Operational notices** (e.g. sethome prompt) can now be delivered privately via `chat_postEphemeral` when `slack.notice_delivery: private` is configured.
3. **`format_message` bug fixes** — markdown images no longer produce broken Slack links, and literal asterisks with spaces (`a * b * c`) are no longer mistakenly italicized.

## Changes

### Commit 1: `fix(gateway/slack): ephemeral ack and routing for slash commands`

 — Two gaps combined to produce the bug:

**Gap 1 fix — Immediate ephemeral ack:**
`handle_hermes_command` now passes `response_type="ephemeral"` and `"Running /cmd…"` text to `ack()`. Previously the bare `await ack()` sent an empty 200 OK, which Slack silently swallowed.

**Gap 2 fix — Ephemeral reply routing via `response_url`:**
- `_handle_slash_command` stashes the Slack `response_url` from the command payload in `_slash_command_contexts` (keyed by `(channel_id, user_id)`) before dispatching.
- `send()` checks for a pending slash context. When found, POSTs to `response_url` with `replace_original: true` to swap the ack with the real reply, keeping it ephemeral.
- Stale contexts garbage-collected on lookup (120s TTL). Non-fatal fallback if POST fails.

### Commit 2: `feat(gateway): private notice delivery and Slack format_message fixes`

Salvaged from PR #9340 by @probepark. Cherry-picked onto current main with original authorship preserved.

| File | What |
|------|------|
| `gateway/config.py` | `_normalize_notice_delivery()` + `GatewayConfig.get_notice_delivery()` with per-platform config bridging |
| `gateway/platforms/base.py` | `send_private_notice()` default implementation (falls through to `send()`) |
| `gateway/platforms/slack.py` | `send_private_notice()` via `chat_postEphemeral` |
| `gateway/run.py` | `_deliver_platform_notice()` helper replaces direct `adapter.send()` for the sethome notice, with private→public fallback |
| `gateway/platforms/slack.py` | `app_mention` handler now forwards to `_handle_slack_message` (safe due to ts-based dedup) instead of no-op |
| `gateway/platforms/slack.py` | `format_message`: negative lookbehind prevents markdown images from becoming broken Slack links; italic regex requires non-whitespace boundaries |

### Commit 3: `chore: add probepark to AUTHOR_MAP`

### Commit 4: `fix(gateway/slack): review fixes — scope ephemeral to commands, user isolation`

Self-review caught and fixed:

1. **Critical — Free-form `/hermes <question>` routed agent reply ephemeral.** The context was stashed unconditionally, so `/hermes what's the weather` would make the full agent response invisible to the channel. **Fix:** Only stash when `text.startswith("/")`.

2. **Critical — Concurrent users on same channel could steal each other's ephemeral context.** `_pop_slash_context` scanned by channel_id only, so User B's response could consume User A's `response_url`. **Fix:** Added a `ContextVar` (`_slash_user_id`) that threads the invoking user's ID from `_handle_slash_command` through to `send()`. `_pop_slash_context` now matches the exact `(channel_id, user_id)` key. ContextVars propagate to child `asyncio.Task`s, so the value survives through `handle_message` → `_process_message_background` → `_send_with_retry` → `send()`.

3. **Medium — `_send_slash_ephemeral` skipped `truncate_message()`.** Long responses could silently fail. **Fixed.**

4. **Warning — Bare `except Exception: pass` in `_deliver_platform_notice`.** **Fixed:** Logs at debug level.

5. **Docs — `app_mention` dedup dependency on shared event ts.** Added comment.

## Files changed

| File | Lines | What |
|------|-------|------|
| `gateway/platforms/slack.py` | +197/-7 | Ephemeral ack, response_url routing, ContextVar isolation, send_private_notice, app_mention fix, fo

…(truncated)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_slack.py`