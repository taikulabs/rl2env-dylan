**fix: resolve three high-impact community bugs (#5819, #6893, #3388)**

## Summary

Resolves the three most-discussed open bugs by community comment count.

### 1. Matrix gateway silently ignores all new messages — #5819 (17 comments)

**Root cause:** `_sync_loop()` in `matrix.py` called `client.sync()` to get raw JSON but **never called `handle_sync()`** to dispatch events to registered callbacks. The `_on_room_message` handler was registered but never fired. Additionally, the loop never tracked/passed the `next_batch` sync token, so every sync was an initial sync instead of incremental.

**Fix:**
- Store `next_batch` from initial sync and pass it as `since=` to subsequent syncs
- Call `client.handle_sync(sync_data)` in the sync loop to dispatch events to handlers
- Updated test to verify `handle_sync` is called and `next_batch` is stored

### 2. Feishu approval error 200340 — #6893 (17 comments)

**Root cause:** Not a code bug — the Feishu code is correct. Error 200340 means "card action callback is not configured for this application." Users need to complete three configuration steps in the Feishu Developer Console that weren't documented.

**Fix:** Added comprehensive setup instructions to `feishu.md`:
- Subscribe to `card.action.trigger` event
- Enable Interactive Card capability in App Features
- Configure Card Request URL (webhook mode)
- Added troubleshooting entry for error 200340

### 3. Copilot GPT-5.4 drifts to OpenRouter and fails — #3388 (7 comments)

**Root cause:** When a Copilot user's primary provider had a transient failure, the fallback chain switched to OpenRouter. But GPT-5.x models require the Responses API path (`codex_responses`), and the fallback only set `codex_responses` for the `openai-codex` provider or direct OpenAI URLs. OpenRouter with GPT-5.x got `chat_completions`, which OpenRouter rejects with `unsupported_api_for_model`.

**Fix:**
- Added `_model_requires_responses_api()` static method that detects GPT-5.x models
- Applied in `__init__` (covers OpenRouter primary users with GPT-5.x)
- Applied in `_try_activate_fallback()` (covers Copilot→OpenRouter drift)
- Fixed stale comment claiming gateway creates fresh agents per message (it caches them via `_agent_cache`)

## Also closed
- #3522 (9 comments) — config preservation during setup: already fixed by `_deep_merge()` pipeline
- #3577 (6 comments) — Claude Pro 1M context: fixed by PR #4747 reactive 429 handling

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_matrix.py`
- `tests/run_agent/test_run_agent_codex_responses.py`