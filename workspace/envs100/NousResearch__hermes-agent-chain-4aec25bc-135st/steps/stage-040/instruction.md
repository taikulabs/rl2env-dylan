**fix(send_message): preserve Slack and Matrix thread targets through channel directory (salvage #26772)**

## Summary
Salvage of #26772 — `send_message` targets like `slack:C123ABCDEF:171.000001` (channel + thread_ts) and `matrix:!room:server.org:$event:server.org` (room + event) resolved from the channel directory were dropping their thread component when round-tripping through `_parse_target_ref()`, sending replies as standalone messages instead of into the thread.

## Changes
- `tools/send_message_tool.py`:
  - Add `_SLACK_THREAD_TARGET_RE` (`<channel>:<thread_ts>`).
  - Recognize Matrix `<room>:$<event>` targets (split on `:$` so server-suffixed event IDs survive).
- `tests/tools/test_send_message_tool.py` — round-trip tests covering Slack thread name → channel + thread_id, Matrix thread name → room + event, plus explicit-target unit tests for both shapes.

## Validation
- `scripts/run_tests.sh tests/tools/test_send_message_tool.py -q` → 115/115 pass.

Original PR: #26772 — credit preserved via rebase-merge.