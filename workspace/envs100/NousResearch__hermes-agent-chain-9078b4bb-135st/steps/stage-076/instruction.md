**fix(telegram): prune stale DM topic binding + disable topic mode when last lane gone**

## Summary
Turning Telegram DM topics off no longer leaves the gateway steering every message back into a deleted topic.

Salvages #31512 (@xxxigm) and adds a proactive cleanup: when the send-fallback prune removes a chat's last topic binding, topic mode for that chat is also disabled so recovery fully stands down.

## Root cause
With DM topic mode on, `_recover_telegram_topic_thread_id` (gateway/run.py) pins each lobby-shaped inbound message to the user's newest bound topic. When a user disables topics **in the Telegram client** (not via `/topic off`), the `enabled=1` flag and the `telegram_dm_topic_bindings` rows survive in state.db. Every send to the now-dead topic hits Bot API `Thread not found`, falls back to a plain send (the char-by-char / disappearing-message symptom), and recovery keeps redirecting the next message to the dead topic id.

## Changes
- `hermes_state.py` — cherry-picked `SessionDB.delete_telegram_topic_binding` (@xxxigm), then extended it: when the prune removes the chat's **last** binding, flip `telegram_dm_topic_mode.enabled` to 0 in the same transaction.
- `plugins/platforms/telegram/adapter.py` — cherry-picked `_prune_stale_dm_topic_binding` + both `Thread not found` fallback sites calling it (@xxxigm).
- tests — 13 original tests (@xxxigm) + 3 new covering the last-binding clear, multi-binding no-op, and unmatched-prune no-op.

## Validation
| | Before | After |
|---|---|---|
| lobby msg after topic deleted | recovers to dead topic 366 | recovery returns None |
| `enabled` after last binding pruned | stays 1 (stuck) | flipped to 0 |
| other healthy topics on prune | — | untouched |

Targeted suites: 106 passed (prune/fallback/topic-mode). E2E against the real `_recover_telegram_topic_thread_id` chain confirms steering is eliminated after the final-binding prune.

. Supersedes #31512 (contributor authorship preserved via rebase-merge).

## Infographic
![Telegram DM topics stale-lane fix](https://v3b.fal.media/files/b/0a9f5aac/KlGF9Xqtgocpk17fggB1i_iZybwyDB.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_prune_stale_topic_binding_31501.py`