**perf(prompt-cache): date-only timestamp + loud gateway-DB roundtrip logging**

## Summary

System prompt is now byte-stable for the full day, and silent gateway-side prefix-cache misses now log loudly instead of disappearing into DEBUG.

The `Conversation started:` line was minute-precision (`%I:%M %p`) — byte-unstable across every rebuild path. Within a CLI session the in-memory cache held, but on the gateway path (fresh `AIAgent` per turn, prompt restored from session DB), any silent failure in the read or write path forced a full re-prefill on every subsequent turn. Local prefix-caching backends (llama.cpp, vLLM) saw it as KV-cache invalidation; remote prefix-caching providers saw it as an Anthropic-style cache miss.

## Changes

| | |
|---|---|
| **C1** Date-only timestamp | `Sunday, May 17, 2026` instead of `Sunday, May 17, 2026 03:42 PM`. System prompt byte-stable for the full day. Credit @iamfoz. |
| **A** Loud DB write logging | `update_system_prompt` failure was `logger.debug`. Now `logger.warning` with the session id and exception. |
| **B** Three-way stored-state read | `session_row.get('system_prompt') or None` collapsed missing / NULL / empty into one path. Now distinguished and warned on null/empty when a continuing session hits them. |
| **Refactor** | Extracted restore logic into `_restore_or_build_system_prompt()` so the prefix-cache path is testable in isolation. |

## Validation

| | Before | After |
|---|---|---|
| System prompt byte-stable within a day | No (minute-precision drifts every 60s) | Yes |
| Silent DB write failure visible in agent.log | No (DEBUG only) | Yes (WARNING) |
| NULL stored system_prompt detected | No (rebuilt forever) | Yes (WARNING + rebuild) |
| Empty stored system_prompt detected | No (rebuilt forever) | Yes (WARNING + rebuild) |

**E2E proof** (live SessionDB, no mocks): fresh `AIAgent` constructed for turn 2 across a 65-second minute-boundary sleep restored byte-identical bytes from the DB. NULL stored prompt fires the new warning. Date-only timestamp survives the rebuild path.

**Tests:**
- `tests/agent/test_system_prompt_restore.py` — 10 new tests covering happy path, fresh build, all silent-failure recovery paths, and byte-stability invariant
- `tests/run_agent/test_run_agent.py::TestBuildSystemPrompt::test_datetime_is_date_only_not_minute_precision` — pins date-only invariant
- Existing `TestSystemPromptStability` / `TestBuildSystemPrompt` / `TestInvalidateSystemPrompt` — all pass (24/24)

## Closes

- #20451 — date-only timestamp (@iamfoz, co-author credited)
- #18547 — stabilize system prompt prefix
- #8689 — stabilize timestamp across compression
- #15866 — timestamp invalidates upstream prefix caching
- #8687 — system prompt timestamp changes after compression

## Notes

The Model and Provider lines are kept in the prompt as-is. They're stable within a session (no `/model` switch) and provide self-identification context. Date-only timestamp closes the only minute-by-minute volatility source.

Within-session invariant audit: every call site of `_build_system_prompt` and every assignment to `_cached_system_prompt` was inventoried. No path mutates the prompt during a healthy session. The cache holds; this PR makes the prompt itself byte-stable across the cache invalidation boundaries (compression event, fresh-agent gateway turn, session resume).