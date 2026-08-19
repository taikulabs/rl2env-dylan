**fix(weixin): content-aware chatty reply splitting (salvage #7587)**

## Summary
Salvages bravohenry's content-aware splitting from PR #7587, adapted to the compact/legacy architecture from #7903.

**What changed:** Compact mode (default) now detects short chatty exchanges (2-6 short lines, no headings/lists/quotes) and splits them into separate WeChat bubbles. Structured content (tables, headings + body, numbered lists) stays in a single message.

### Salvaged from
| PR | Author | Contribution |
|----|--------|-------------|
| #7587 | @bravohenry | Content-aware chatty detection + structured preservation |