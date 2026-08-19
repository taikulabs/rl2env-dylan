**fix(gateway): support Telegram MarkdownV2 expandable blockquotes**

## What does this PR do?

Updates the Telegram `format_message()` blockquote conversion to support **MarkdownV2 expandable blockquotes** (`**> ... ||`) while preserving existing behavior for regular blockquotes (`>`, `>>`, `>>>`).

Previously, the `**>` prefix and trailing `||` end marker were escaped by the MarkdownV2 sanitizer, causing expandable blockquotes to render as literal characters instead of Telegram's native expandable quote UI.

## Related Issue

No related issue — this is a small, self-contained bug fix.