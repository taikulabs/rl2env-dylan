**fix: show full last assistant response when resuming a session**

## Summary

When resuming a session with `--resume` or `-c`, the last assistant response was truncated to 200 chars / 3 lines — identical to older messages in the recap. Users had to waste tokens re-asking "resend your latest response" just to see where they left off.

Now the last assistant message in the recap panel is shown **in full** with non-dim styling, making it visually distinct and immediately readable. Earlier messages remain compact.

Reported by @uzairansar.

## Changes

**`cli.py`** — `_display_resumed_history()`:
- Track un-truncated text (`_last_asst_full`) alongside truncated entries during collection
- After history trimming, replace the last assistant entry with its full version using the `assistant_last` role tag
- Render `assistant_last` entries with bold, non-dim styling so the last response stands out from the dim recap

**`tests/cli/test_resume_display.py`**:
- Updated `test_long_assistant_message_truncated` and `test_multiline_assistant_truncated` to use multi-turn histories (testing non-last message truncation)
- Added `test_last_assistant_response_shown_in_full` — 500-char response shown without truncation
- Added `test_last_assistant_multiline_shown_in_full` — 20-line response shows all lines