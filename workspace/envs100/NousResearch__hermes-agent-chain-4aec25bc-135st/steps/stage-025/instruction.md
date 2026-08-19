**feat(status): append session recap to /status output (salvage of #18587)**

## Summary
Salvage of #18587 — folded into `/status` instead of a standalone `/recap` command.

Adds a pure-local recap of recent session activity (turn counts, tools used, files touched, last user ask, last assistant reply) appended to the existing `/status` output. Useful when juggling multiple sessions and you want a one-glance reminder of where this one left off.

Inspired by Claude Code 2.1.114's `/recap`, but kept off the command menu since we already have five info commands (`/status`, `/usage`, `/insights`, `/history`, `/agents`) and the recap belongs naturally inside `/status`. Pure local computation: no LLM call, no auxiliary model, no prompt-cache invalidation, instant and free.

## Why fold into `/status` instead of adding `/recap`
- `/status` already answers "where am I" (session metadata)
- `/usage` answers "what did this cost" (tokens, rate limits)
- `/insights` answers "patterns across sessions" (cross-session analytics)
- `/history` answers "show me everything verbatim" (CLI only)

`/recap` would answer "what was this session about" — which is the natural continuation of `/status` ("where am I → what was I doing"). Folding avoids adding a 6th info command users could miss.

## Changes
- `hermes_cli/session_recap.py` (+316): the pure `build_recap(messages, *, session_title, session_id, platform) → str` helper from #18587. Unchanged from the original PR — handles multimodal content blocks, dict/string tool_call arguments, cwd-relative path shortening, 20-turn recency window.
- `tests/hermes_cli/test_session_recap.py` (+180): 13 unit tests covering empty history, header variants, turn counting, tool-call aggregation, file-edit tracking, truncation, multimodal flattening, dict/string argument forms, malformed entries.
- `cli.py` (+18): `_show_session_status()` appends the recap after the existing metadata block. Wrapped in defensive try/except so the recap can never break `/status`.
- `gateway/run.py` (+18): same pattern in `_handle_status_command()`, using `session_store.load_transcript(session_id)` for the message list.

Dropped from the original PR: the `/recap` `CommandDef` entry, `ACTIVE_SESSION_BYPASS_COMMANDS` membership, Level-2 early-intercept bypass, CLI `_handle_recap_command`, gateway `_handle_recap_command`, and the docs page entry. `/status` already covers both surfaces and is already in `ACTIVE_SESSION_BYPASS_COMMANDS`.

## Validation
| | Result |
|---|---|
| `tests/hermes_cli/test_session_recap.py` | 13/13 |
| `tests/hermes_cli/` + `tests/gateway/` (status / command / recap) | 1022/1022 |
| E2E (real `build_recap` on a realistic mixed history) | All recap fields render: title, scope, tools used, files touched, last ask, last reply |

## Example `/status` output
```
Hermes CLI Status

Session ID: abc12345
Model: claude-opus-4.7 (openrouter)
Created: 2026-05-15 21:56
Last Activity: 2026-05-16 04:12
Tokens: 142,338
Agent Running: No

Session recap — Fix tool_calls regression
  Recent: 2 user turns / 3 assistant replies, 3 tool results
  Tools used: patch×1, read_file×1, search_files×1
  Files touched: run_agent.py
  Last ask: great, please also add a test for this specific scenario
  Last reply: Fixed! The tool_calls were being dropped due to a missing branch in _sanitize_messages. All 142 tests pass.
```

## Source
Inspired by Claude Code 2.1.114's `/recap` — https://code.claude.com/docs/en/whats-new/2026-w17. Originally scouted in #18587.