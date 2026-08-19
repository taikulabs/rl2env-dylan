**fix(acp): route Zed thoughts to reasoning + polish tool/context rendering**

Salvage of #18578 onto current main. All 7 commits cherry-picked from @HenkDz with authorship preserved.

## Summary
Zed (and other ACP clients) now show provider reasoning in the thought pane instead of Hermes' kawaii waiting strings, get a live context-usage indicator, and render ~35 tool types as human-readable panes instead of raw JSON.

## Changes
- `acp_adapter/server.py`: `thinking_callback=None`; route provider reasoning deltas via `reasoning_callback`; stream assistant response through `stream_delta_callback` and skip the duplicate `final_response` send when already streamed.
- `acp_adapter/server.py`: emit ACP `usage_update` (context size + estimated used tokens) after new/load/resume session and every prompt; powers Zed's circular context indicator.
- `acp_adapter/server.py`: `/context` slash command now shows provider, token pressure, and compression-threshold guidance.
- `acp_adapter/server.py`: `session/load` and `session/resume` replay also reconstructs tool-call `start`/`complete` events so loaded threads look like the original.
- `acp_adapter/tools.py`: polished rendering for ~35 tool types (todo, read_file, search_files, execute_code, skill_view/list/manage, web_search, web_extract, terminal, process, browser_*, kanban_*, feishu_*, ha_*, yb_*, cronjob, send_message, delegate_task, etc.); `raw_output=None` on polished tools so Zed doesn't double-show a raw accordion.
- Tests: +456 lines across `tests/acp/test_server.py`, `test_tools.py`, `test_mcp_e2e.py`.

## Validation
- `scripts/run_tests.sh tests/acp/ -q` → 206 passed
- All 7 contributor commits cherry-picked cleanly onto current main with authorship preserved (rebase-merge this PR).

## Closes
. Credit to @HenkDz for the entire implementation.