**fix(weixin): keep multi-line messages in single bubble by default**

## Summary

The Weixin adapter was splitting responses at every top-level newline, causing notification spam — up to 70 API calls for a single long markdown response. Six independent contributors submitted PRs to fix this. This salvages the best aspects of all six.

### What changed

**Compact mode (new default):**
- Messages under the 4000-char limit stay as a single bubble even with multiple lines, paragraphs, and code blocks
- Only oversized messages get split at logical markdown boundaries
- 0.3s inter-chunk delay between chunks prevents WeChat rate-limit drops

**Legacy mode (opt-in):**
- Set `split_multiline_messages: true` in `platforms.weixin.extra` config
- Or set `WEIXIN_SPLIT_MULTILINE_MESSAGES=true` env var
- Restores the old per-line splitting behavior

### Files changed (4 files, +96/-27)
- `gateway/platforms/weixin.py` — split function now supports compact/legacy modes via `split_per_line` param; `_coerce_bool` helper; config wiring; inter-chunk delay in `send()`
- `gateway/config.py` — env var override for `WEIXIN_SPLIT_MULTILINE_MESSAGES`
- `tests/gateway/test_weixin.py` — updated assertions for compact default; added legacy mode test; added env var config test
- `website/docs/user-guide/messaging/weixin.md` — updated chunking docs, config table, feature description

### Salvaged from
| PR | Author | Contribution |
|----|--------|-------------|
| #7797 | @guantoubaozi | Simplest core fix — remove `"\\n" not in content` guard |
| #7792 | @luoxiao6645 | Aggressive cleanup approach, single-message-under-limit |
| #7838 | @qyx596 | Config toggle + env var + docs + `_coerce_bool` |
| #7825 | @weedge | Inter-chunk delay (0.3s) for rate-limit protection |
| #7784 | @sherunlock03 | Clean minimal fix |
| #7773 | @JnyRoad | Short multiline single-bubble fix |