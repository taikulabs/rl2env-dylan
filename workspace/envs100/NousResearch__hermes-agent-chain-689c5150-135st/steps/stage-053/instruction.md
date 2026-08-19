**fix(run_agent): refresh activity during streaming responses**

## Summary

Salvage of PR #8836 by @yongtenglei onto current main. .

Long-running streamed responses were being incorrectly killed by the gateway/cron inactivity timeout even while tokens were actively arriving. The root cause: `_touch_activity()` (which feeds `get_activity_summary()` polled by the external timeout) was either called only on the first chunk (chat completions) or not at all (Anthropic, Codex, Codex fallback).

### Changes

Adds `self._touch_activity("receiving stream response")` on every chunk/event in all four streaming paths:

| Path | Before | After |
|------|--------|-------|
| Chat completions | First chunk only (`_first_chunk_seen` flag) | Every chunk |
| Anthropic Messages | Never (only `last_chunk_time`) | Every event |
| Codex stream | Never | Every event |
| Codex fallback stream | Never | Every event |

`_touch_activity` is trivially cheap (two attribute assignments), so per-chunk calling has no performance impact.

### Follow-up fix

Fixed test class organization from original PR — `TestAnthropicStreamCallbacks` was inserted in the middle of `TestCodexStreamCallbacks`, causing two codex tests to end up in the wrong class. Moved the Anthropic class after all codex tests.