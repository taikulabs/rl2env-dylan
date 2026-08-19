**fix(telegram): clip mid-stream overflow instead of splitting**

## Summary
Telegram streamed replies that grow past 4096 chars no longer spawn an infinite nested-reply duplication loop.

Root cause: `edit_message`'s overflow split ran on **every** streamed edit (`finalize=False` included). Splitting moves the active message ID to a continuation, so the next accumulated-token edit re-splits the full text — looping once per token after the limit is hit.

## Changes
- `plugins/platforms/telegram/adapter.py`: gate `_edit_overflow_split` on `finalize`. Mid-stream, truncate to a single preview message via new `_truncate_stream_overflow_preview` helper (keeps editing the same ID). Fixes both the pre-flight path and the reactive `message_too_long` catch. Full content is still split-and-delivered on `finalize=True`.
- `tests/gateway/test_telegram_format.py`: flip the existing continuation-split test to `finalize=True` (splitting is now finalize-only), add two mid-stream truncation tests.

## Validation
| | Before | After |
|---|---|---|
| 7 growing oversized mid-stream edits | N continuation messages (loop) | 0 continuations, message_id stable |
| finalize=True | splits | splits, full content delivered (2 continuations) |

Targeted tests: 4 passed. E2E (real `edit_message`, mocked bot): mid-stream continuation sends = 0, ID stays put, finalize delivers full content.

## Credit
Salvaged from #50408 by @Tranquil-Flow (authorship preserved via rebase-merge). . Supersedes duplicate  (@liuhao1024, earliest submitter), #48718 (@kyssta-exe), #51266 (@RichardAtCT) — those targeted the pre-refactor path `gateway/platforms/telegram.py`, which no longer exists.

## Infographic
![Telegram stream overflow duplication loop fixed](https://v3b.fal.media/files/b/0a9f8c9c/RALkroY8yHTHRE4SS5UXN_s8Q0e31E.png)