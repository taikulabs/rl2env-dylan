**fix(discord): prevent double dispatch via thread-starter dedup**

## Summary
A single Discord message no longer triggers two agent runs / two responses when auto-threading is enabled.

Root cause: with `DISCORD_AUTO_THREAD` defaulting to `true`, a user's channel message triggers `_auto_create_thread()`. Discord then fires a **second `MESSAGE_CREATE`** for the thread-starter message, which (per Discord's API + discord.py) **shares the same id as the thread** and can arrive as `type=default` — bypassing both the `message.id` dedup and the message-type filter, producing a duplicate `_handle_message` dispatch.

Fix: after `_auto_create_thread()` succeeds, pre-seed the existing `_dedup` cache with `str(thread.id)`. When the duplicate thread-starter event arrives, the dedup guard at the top of `on_message` drops it before it reaches `_handle_message`.

## Changes
- `plugins/platforms/discord/adapter.py`: one line — `self._dedup.is_duplicate(str(thread.id))` immediately after thread creation, reusing the existing TTL-based `MessageDeduplicator`. No new state, no core touch.
- `tests/gateway/test_discord_double_dispatch.py`: 12 tests covering thread-starter dedup, no-seed-on-failure, auto-thread-disabled, `text_batch_delay=0` path, RESUME replay preservation, and no-over-blocking.

## Validation
| Check | Result |
|---|---|
| Root cause confirmed (Discord docs: thread.id == starter message id) | yes |
| Contributor tests | 12 passed |
| E2E (real `MessageDeduplicator`, 4-step Discord event sequence) | thread-starter dropped; unrelated msg passes; user msg passes first; pre-seed wired in source |
| ruff | clean |

E2E walked the genuine sequence with the real dedup class: user message (passes) → pre-seed `thread.id` → thread-starter dup with `id == thread.id` (**dropped**) → unrelated later message (**passes**, no over-blocking).

Deterministic fix — neutralizes the exact ID the duplicate event carries, with no false-positive risk.

Salvage of #51129 — cherry-picked to preserve @manus-use's authorship.