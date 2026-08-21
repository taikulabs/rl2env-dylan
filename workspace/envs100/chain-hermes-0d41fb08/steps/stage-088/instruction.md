**fix: activate fallback provider on repeated empty responses + user-visible status**

## Problem

When models return empty responses (no content, no tool calls, no reasoning), Hermes retries 3 times **silently** then falls through to `(empty)` — without ever trying the fallback provider chain. Users on GLM-4.5-Air and similar models experienced what appeared to be a complete hang, especially in gateway (Telegram/Discord) contexts where the silent retries produced zero feedback.

**Root cause from #7180:** The empty-response retry path at the conversation loop level (after parsing a valid API response with no content) did not call `_try_activate_fallback()`. Only the API-level retry path (rate-limit, malformed response) triggered fallback. This meant a model consistently returning empty responses would never switch to a backup provider — even when one was configured.

## Fix

### 1. Fallback activation after empty retry exhaustion
After 3 empty retries, attempt `_try_activate_fallback()` before falling through to `(empty)`. If a fallback provider is available and activates successfully:
- Reset `_empty_content_retries` to 0
- Continue the conversation loop with the new provider
- The user sees the conversation continue seamlessly

### 2. User-visible status across all interfaces
Replace all `_vprint()` calls in recovery paths with `_emit_status()`, which surfaces messages through both:
- **CLI** — `_vprint(force=True)`, always visible regardless of quiet mode
- **Gateway** (Telegram, Discord, Slack, etc.) — `status_callback("lifecycle", ...)` → `adapter.send()`, delivered as a message to the user

Users now see at each stage:
- `⚠️ Empty response from model — retrying (1/3)` during retries
- `⚠️ Model returning empty responses — switching to fallback provider...`
- `↻ Switched to fallback: <model> (<provider>)` on successful switch
- `❌ Model returned no content after all retries and fallback attempts.` when nothing works

### 3. Proper logging throughout
Added `logger.warning()` with model name, provider, and retry counts to all empty response paths. Previously these were either `logger.debug` (invisible) or only `_vprint` (no log file trace).

### Recovery paths upgraded
| Path | Before | After |
|------|--------|-------|
| Empty retry loop (3 attempts) | `_vprint(force=True)` only | `_emit_status()` + `logger.warning()` |
| Retry exhaustion | Fall to `(empty)` immediately | Try `_try_activate_fallback()` first |
| Thinking-only prefill | `_vprint()` (no force) | `_emit_status()` + `logger.info()` |
| Prior-turn content fallback | `logger.debug()` | `logger.info()` + `_emit_status()` |
| Final `(empty)` terminal | `_vprint()` only | `_emit_status()` + `logger.warning()` |

## Tests

3 new tests added:
- `test_empty_response_triggers_fallback_provider` — verifies fallback activation after 3 empty retries, fallback model produces content
- `test_empty_response_fallback_also_empty_returns_empty` — verifies graceful degradation when fallback also returns empty
- `test_empty_response_emits_status_for_gateway` — verifies `_emit_status` is called during retries (3 retry messages + 1 failure message)

All 247 tests in `test_run_agent.py` pass.

## Changes
| File | +/- |
|------|-----|
| `run_agent.py` | +73/-15 |
| `tests/run_agent/test_run_agent.py` | +105 |

Addresses #7180.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_run_agent.py`