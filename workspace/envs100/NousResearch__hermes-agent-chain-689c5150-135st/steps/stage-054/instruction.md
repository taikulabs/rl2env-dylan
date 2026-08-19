**fix(matrix): suppress streaming cursor artifacts on Matrix**

## Summary

Salvage of #8621 by @helix4u. Cherry-picked onto current main with conflict resolution.

Matrix clients (Element, etc.) render the streaming cursor character (▉) as visible white-box/tofu artifacts. This was reported by a user after a recent update — the cursor leaks through as both standalone messages and appended to edited streaming content.

## Changes

**Two layers of fix:**

1. **`gateway/run.py`** — Suppresses the cursor specifically for Matrix by setting `_effective_cursor = ""` when `source.platform == Platform.MATRIX`. Integrates with the existing `_effective_cursor` pattern (which already handles WeChat's `SUPPORTS_MESSAGE_EDITING = False` case).

2. **`gateway/stream_consumer.py`** — Adds a defensive guard in `_send_or_edit()` that strips the cursor from text and skips sending if only whitespace remains. Good for all platforms.

## Conflict resolution

The PR was 92 commits behind main. The only conflict was in `gateway/run.py` where the cursor assignment changed — main now has `_effective_cursor` (added for WeChat support), while the PR used inline `cursor="" if ... else _scfg.cursor`. Resolved by adding the Matrix condition as a separate block after the existing `_effective_cursor` assignment.

## Tests

- 46 passed in stream_consumer + progress_topics test files
- New unit test: cursor-only update skips send
- New integration test: Matrix streaming content never contains ▉