**fix(gateway): confirm final delivery before suppressing send**

## Summary
The gateway no longer drops the final reply when a context-compression session split lands exactly at the response boundary.

Root cause: `response_previewed=True` was treated as proof the final answer reached the user. During a split, the interim callback delivers unrelated commentary (e.g. "I'll inspect the repo first.") — not the final answer — so the real send was suppressed and the reply was persisted to the child session JSON but never sent to chat (Feishu/Discord/Telegram/etc). .

## Changes
- `gateway/stream_consumer.py`: track exact delivered commentary text (`_delivered_commentary_texts`) and add `has_delivered_text(text)` — compares the requested final text against the visible streamed prefix and the actually-delivered commentary.
- `gateway/run.py`: add `_stream_confirmed_final_delivery()` — only suppress the normal final send when the consumer confirms final delivery (`final_response_sent` / `final_content_delivered`), or when `previewed` AND that *exact* final text was confirmed delivered. Applied to both the queued-follow-up path and the final-send path. The existing `final_content_delivered` and plugin-`transform` branches are preserved.

## Validation
| Scenario | Before | After |
|---|---|---|
| split: commentary previewed, final ≠ commentary | suppressed → reply dropped | not suppressed → reply sent |
| preview was the exact final text | suppressed | suppressed (no dup) |
| streamed (`final_response_sent`) | suppressed | suppressed |
| no stream consumer | sent | sent |

Targeted suite: `tests/gateway/test_run_progress_topics.py` + `tests/gateway/test_stream_consumer.py` → 133 passed, 0 failed. Logic re-verified end-to-end with real imports against the four scenarios above.

Salvaged from #14391 by @sgaofen onto current `main`; authorship preserved. Conflicts (since-added `final_content_delivered` signal + `_send_commentary` refactor) resolved in favor of current `main` plus the contributor's fix.

## Infographic

![pr-14391-session-split-final-reply](https://v3b.fal.media/files/b/0aa038ae/pmY-3PsuNHRYEjVguKFTV_aypwgzqC.png)