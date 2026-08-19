**fix(discord): split oversized final edits, truncate mid-stream previews**

## Summary
Discord streaming/tool-progress replies over 2,000 chars are now delivered in full instead of being silently clipped. `DiscordAdapter.edit_message` clipped any oversized formatted payload to `[:1997] + "..."` and returned `success=True`, so the stream consumer believed the whole reply landed and stopped — the user lost everything past the cap and perceived the agent as quitting mid-task.

Root cause: `edit_message` had no overflow handling. The `SendResult` split contract (`continuation_message_ids`, `partial_overflow`) and the stream consumer's split handling already existed for Telegram; Discord never used them.

## Changes
- **`plugins/platforms/discord/adapter.py`** — `edit_message` is overflow-aware, with a new `_edit_overflow_split` helper:
  - **`finalize=True`** → split-and-deliver: edit chunk 1 in place (fence-aware `truncate_message`, `(1/N)` indicators), send chunks 2..N as reply-threaded continuations. Returns `message_id` = last visible chunk + `continuation_message_ids` so the consumer keeps editing the most recent chunk and can clean them all up.
  - **`finalize=False` (mid-stream)** → truncate a one-message preview **in place, never split**. A mid-stream split moves the edit target to a continuation and the next accumulated-token tick re-splits → infinite duplication. This is the Telegram **#48648** lesson the earlier port (#27961 / #23703) predated and would have re-introduced.
  - **Reactive `50035` "2000 or fewer in length"** on the edit runs the same branch logic (formatter inflation past the cap). A non-length 50035 (bad reply reference) is *not* treated as overflow.
  - **Partial continuation failure** still reports `success=True` with a `partial_overflow` raw_response so the consumer retries the tail rather than marking a clipped reply complete. Only a first-chunk edit failure returns `success=False`.
- **`tests/gateway/test_discord_edit_message_overflow.py`** — 13 regression tests: happy path, mid-stream truncate-don't-split, final split byte-coverage + reply threading + last-id contract, first-chunk failure propagation, partial-delivery contract, reactive 50035 detection, and the length-error detector.

## Validation
| | Before | After |
|---|---|---|
| Streaming edit > 2000 chars | clipped to `…`, `success=True` | preview truncated in place, no split, no loop |
| Final edit > 2000 chars | clipped, tail lost | split across edit + reply-threaded continuations, full text delivered |
| `message_id` after split | n/a | points at last visible chunk |
| Mid-stream re-split loop | would occur on a naive port | structurally impossible (split gated on `finalize`) |

- 13/13 new tests pass; existing Discord send/reply/format + stream-consumer suites green (152 tests).
- E2E: 7 streaming ticks over the cap created 0 continuations and kept the original edit target (no loop); finalize delivered all 3 chunks with the tail marker intact and `message_id` = last continuation.

Note: #27881's reporter symptom (turn ends after only *stating* intent) was the real root cause, fixed separately by merged #53943. This is the distinct silent-truncation defect those contributors correctly identified.

Credits: this fix was independently identified by @xxxigm and @AhmetArif0 (#23703, earliest). Both are co-authored on the commit; their PRs predated the #48648 split-gating lesson, so this is a corrected, current-tree implementation of their finding.

## Infographic

![discord-edit-overflow-split](https://v3b.fal.media/files/b/0aa05c77/1tUETX6882ySZcuydAqr4_ur2ohrJZ.png)