**fix(gateway): replace os.environ session state with contextvars + fix skill frontmatter truncation**

## Summary

Salvages PR #7391 and PR #7394 by @0xFrank-eth onto current main.

### Fix 1: Concurrent session env cross-contamination ()

When two gateway messages arrived concurrently, `_set_session_env` wrote `HERMES_SESSION_PLATFORM`, `HERMES_SESSION_CHAT_ID`, `HERMES_SESSION_CHAT_NAME`, and `HERMES_SESSION_THREAD_ID` into the process-global `os.environ`. Because asyncio tasks share the same process, Message B's values silently overwrote Message A's before its tools finished executing — background-task notifications and tool calls routed to the wrong thread/chat.

**Fix:** Replace `os.environ` with Python's `contextvars.ContextVar`. Each asyncio task (and any `run_in_executor` thread it spawns) gets its own copy. `get_session_env()` falls back to `os.environ` for backward compatibility with CLI, cron, and tests.

**Improvements over original PR:**
- Covers 3 additional consumer sites the original PR missed:
  - `terminal_tool.py` notify_on_complete block (lines 1423-1426) — same race, same file
  - `agent/skill_utils.py` — platform detection for per-platform skill disabling
  - `agent/prompt_builder.py` — platform hint for skill listing cache key
- `get_session_env()` falls back to `os.environ` automatically — eliminates the need for verbose try/except ImportError blocks at every callsite
- `clear_session_vars()` handles `None` tokens gracefully (for tests that mock `_set_session_env`)
- Tests fully rewritten for the new contextvar-based API

### Fix 2: SKILL.md frontmatter silently truncated at 2000 chars ()

`_parse_skill_file()` sliced file content to 2000 chars before parsing YAML frontmatter. Skills with long frontmatter had the closing `---` cut off, causing `parse_frontmatter` to return empty metadata. The skill appeared to load but never activated.

**Fix:** Remove the `[:2000]` slice. Upgrade parse-failure log level from DEBUG to WARNING.

**Staleness adaptation:** Original PR targeted two functions, but `_read_skill_conditions` no longer exists on main. Only the one remaining site was fixed.

## Files changed (10)

| File | Change |
|------|--------|
| `gateway/session_context.py` | **New** — ContextVar definitions + set/clear/get helpers |
| `gateway/run.py` | `_set_session_env` returns tokens, `_clear_session_env` accepts them |
| `tools/cronjob_tools.py` | `os.getenv` → `get_session_env` |
| `tools/send_message_tool.py` | `os.getenv` → `get_session_env` (2 sites) |
| `tools/skills_tool.py` | `os.getenv` → `get_session_env` |
| `tools/terminal_tool.py` | `os.getenv` → `get_session_env` (2 blocks) |
| `tools/tts_tool.py` | `os.getenv` → `get_session_env` |
| `agent/skill_utils.py` | `os.getenv` → `get_session_env` |
| `agent/prompt_builder.py` | `os.environ.get` → `get_session_env` + remove `[:2000]` slice + logger.warning |
| `tests/gateway/test_session_env.py` | Rewritten for contextvar API |

## Test results

160 targeted tests pass (gateway, cron, tools, skills). Pre-existing failures in test_reasoning_command and test_run_progress_topics are unrelated (`_session_model_overrides` missing from `object.__new__()` test helpers — known pitfall #17).