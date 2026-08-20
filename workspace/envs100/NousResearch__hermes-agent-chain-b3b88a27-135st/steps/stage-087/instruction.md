**fix(discord): shield text-batch flush from follow-up cancel**

## Summary
A follow-up chunk of a split Discord message can no longer cancel the in-flight dispatch of the previous chunk. Previously the chain `_enqueue_text_event → prior_task.cancel() → CancelledError into await handle_message` aborted the agent's streaming request, leaving the user with a truncated or missing reply.

## Scenario
User sends a 3000-char prompt. Discord splits it at 2000 chars into two messages. Chunk 1 lands → flush task scheduled. Chunk 1's flush delay expires → pops chunk 1, enters `await self.handle_message(chunk_1)`. Chunk 2 lands during that in-flight dispatch → `_enqueue_text_event` calls `prior_task.cancel()` → CancelledError propagates from the flush task down into `handle_message` → base adapter session processing → agent's `run_conversation` → the streaming HTTP request. Response aborts.

## Fix
- `gateway/platforms/discord.py`: wrap the inner call in `asyncio.shield(self.handle_message(event))` so the cancel of the outer flush task doesn't reach the inner dispatch. Add an `except asyncio.CancelledError` clause so the outer task still exits cleanly when cancel arrives during the sleep window (before `pop`) — that semantic is unchanged.
- Follow-up chunks still get their own flush task and are dispatched via the normal pending-message / active-session machinery in `base.py`. Nothing is lost.

## Validation
| | Before | After |
|---|---|---|
| Follow-up chunk during in-flight handle_message | chunk 1's handle_message receives CancelledError | chunk 1's handle_message runs to completion |
| Cancel during the sleep window (before pop) | flush task exits, new task takes the aggregated batch | same |
| Normal single-chunk flush | works | works |
| Adaptive split-delay for near-2000-char chunks | works | works |

Regression-guard: `test_shield_protects_handle_message_from_cancel` uses a distinct `first_handle_cancelled` event so the assertion fails cleanly when the shield is missing. Verified — stashing the fix makes the test FAIL with the exact message we want; re-applying makes it pass.

Targeted: `test_text_batching.py` 16/16, `test_discord_send.py` 17/17, `test_discord_reactions.py` 14/14, `test_discord_reply_mode.py` 26/26 — 73 total.

Live E2E against the live-loaded `DiscordAdapter`:
```
=== _flush_text_batch in live-loaded DiscordAdapter ===
asyncio.shield wrapping handle_message: OK
CancelledError clause for early-cancel path: OK

=== End-to-end cancel test ===
  first_handle_cancelled: False  (expected: False)
  first_handle_completed: True   (expected: True)
```

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_text_batching.py`