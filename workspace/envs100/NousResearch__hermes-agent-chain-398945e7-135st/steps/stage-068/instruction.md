**feat(gateway): auto-delete slash-command system notices after TTL**

Auto-deletes slash-command reply messages ("✨ New session started!", "♻ Restarting gateway…", "⚡ Stopped.", "⚡ YOLO mode ON/OFF") after a configurable TTL on platforms that support message deletion. Requested by @charlesmcdowell on Twitter — tool bubbles are useful to watch in real time, but these system notices clutter the thread once the agent finishes.

## Changes
- `gateway/platforms/base.py`: new `EphemeralReply(str)` sentinel (subclasses `str` so existing `'X' in response` / `response.startswith(...)` call sites keep working; `isinstance()` still discriminates for the send path). `_unwrap_ephemeral()` helper + `_schedule_ephemeral_delete()` task spawner. Wired into `_process_message_background` **and** the two busy-session bypass paths (L2452 and L2552 — used when `/stop`, `/restart`, `/approve` bypass the running-agent guard).
- `gateway/run.py`: wrapped 8 highest-noise return sites — `/new`, `/reset`, `/stop` (×3), `/yolo on/off`, `/restart` success + "already in progress". Draining notices and `/help` output stay as plain strings (informational content users want to read).
- `hermes_cli/config.py`: `display.ephemeral_system_ttl` (int seconds, default `0` = disabled).
- `tests/gateway/test_ephemeral_reply.py`: 13 unit tests covering unwrap, scheduling, capability gate, and full `_process_message_background` flow.

## Behavior

| | Before | After |
|---|---|---|
| Default config (`ephemeral_system_ttl: 0`) | System notices stay forever | Same — no behavior change |
| `ephemeral_system_ttl: 300` on Telegram | System notices stay forever | Delete after 5 min; agent responses never touched |
| `ephemeral_system_ttl: 300` on Discord/Slack/iMessage | N/A | Silent no-op — adapters without `delete_message` override keep the message in place |
| Per-reply override (`EphemeralReply(text, ttl_seconds=60)`) | — | Wins over config default |

## Capability gate

TTL is only honored when `type(adapter).delete_message is not BasePlatformAdapter.delete_message` — same pattern used at `gateway/run.py:11424` for progress-bubble cleanup. Currently only Telegram overrides it. Discord could be added in a follow-up (`channel.delete_messages()` exists); WhatsApp / iMessage don't have a delete API so they just ignore the TTL cleanly.

## Opt-in scope

Only the following system notices are wrapped — everything else stays plain:
- `/new` and `/reset` → "✨ New session started!" / "✨ Session reset!…"
- `/stop` → "⚡ Stopped. You can continue this session." (×3 return paths)
- `/yolo` → "⚡ YOLO mode ON/OFF…"
- `/restart` → "♻ Restarting gateway…" + "⏳ Gateway restart already in progress…"

Things **not** wrapped (deliberate):
- `/help`, `/commands`, `/status`, `/queue` — reference content users read
- "⏳ Draining N active agent(s) before restart…" — informational about work in flight
- Agent responses and streamed content — never touched by this path
- Tool progress bubbles — already have their own lifecycle via `progress_task` / `progress_msg_id`

## Validation

- Targeted: `scripts/run_tests.sh tests/gateway/test_ephemeral_reply.py` → 13 passed.
- Regression-sensitive: full `tests/gateway/` → 4420 passed, 0 related failures (one pre-existing `test_teams.py::test_send_typing` failure confirmed present on unmodified `main`).
- E2E with real `_process_message_background` + real config.yaml + TTL=3s: send went out with unwrapped text, `delete_message` fired after the TTL with the correct `message_id`.
- E2E with default config (TTL=0): message sent, no delete scheduled — confirmed backward-compat.

## Caveats (named upfront)

- Telegram's `deleteMessage` only works for the bot's own messages ≤48h old — well within any reasonable TTL.
- In Telegram groups the bot needs the "Delete messages" permission; failures are logged at debug level and the message just stays.
- No persistence: if the gateway restarts during the TTL window, the pending delete is lost. Accepting best-effort here — the alternative (disk-backed queue) is overkill for cosmetic cleanup.

…(truncated)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_ephemeral_reply.py`