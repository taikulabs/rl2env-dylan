**fix(discord): close two low-severity adapter races**

## Summary
Two small, narrow races in `gateway/platforms/discord.py`, bundled since they're adjacent in the adapter.

### 1. `on_message` vs `_resolve_allowed_usernames` (startup window)
`DISCORD_ALLOWED_USERS` accepts both numeric IDs and raw usernames. On connect, `_resolve_allowed_usernames` fetches guild members (multi-second call) to swap usernames for IDs. `on_message` can fire during that window; `_is_allowed_user` compares the numeric `author.id` against a set that may still contain raw usernames — legitimate users get silently rejected for a few seconds after every reconnect.

**Fix:** `on_message` awaits `_ready_event` (30s timeout) when it isn't already set. `on_ready` sets the event after the resolve completes. No-op in steady state; only the startup / reconnect window ever blocks.

### 2. `join_voice_channel` check-and-connect
The existing-connection check at `_voice_clients.get()` and the `channel.connect()` call straddled an `await` boundary with no lock. Two concurrent `/voice channel` invocations could both see None and both call `connect()`; discord.py raises `ClientException` on the loser. Same race class for `leave_voice_channel` racing `_voice_timeout_handler`.

**Fix:** per-guild `asyncio.Lock` (`_voice_locks` dict with lazy alloc via `_voice_lock_for`). Both `join_voice_channel` and `leave_voice_channel` run under the lock. Sequential within a guild, still fully concurrent across guilds.

## Changes
- `gateway/platforms/discord.py`: `_ready_event` wait in `on_message`, `_voice_locks` field + `_voice_lock_for` helper, lock wraps in `join_voice_channel` and `leave_voice_channel`.
- `tests/gateway/test_discord_race_polish.py`: 2 regression cases.

## Validation
| | Before | After |
|---|---|---|
| Message arrives during on_ready username resolution | allowlist rejects (string vs numeric compare) | waits ≤30s, then proceeds with resolved set |
| Two concurrent `/voice channel` on same guild | `ClientException: Already connected` on loser | serialized; only one `connect()` fires |
| `join` + `leave` racing | interleaved state mutations | serialized per-guild |
| Any of the above across different guilds | works | still concurrent (lock is per-guild) |

Regression-guard: against unpatched code, both new tests fail. With the fix they pass.

Targeted: `test_discord_race_polish.py` 2/2, plus 53 other Discord tests (send, bot_filter, reactions, text_batching, connect, bot_auth_bypass, allowed_mentions, slash_commands) — 118 total green.

## Severity
LOW. The first is a startup-only window affecting username-based allowlists; the second is a narrow exception on simultaneous voice commands. Shipping because both fixes are small and the polish is worth it with the broader gateway audit work.