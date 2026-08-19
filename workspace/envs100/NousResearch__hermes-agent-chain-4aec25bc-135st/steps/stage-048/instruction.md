**feat(acp): add session edit auto-approval modes (salvage of #27034)**

Salvage of #27034 by @HenkDz onto current main.

## Summary
Move the ACP edit-approval policy selector off `config_options` and onto ACP session modes (Default / Accept Edits / Don't Ask) so Zed's model picker stays visible, and surface the structured edit diff on the tool-start card when an edit is going to be auto-approved.

This is the full edit-approval stack — supersedes #26626. Contains:
- `feat(acp): require approval for editor file edits` (was #26626)
- `fix(acp): avoid duplicate edit approval diffs`
- `feat(acp): add session-scoped edit auto-approval`
- `fix(acp): use modes for edit auto-approval`

## Changes
- `acp_adapter/edit_approval.py` (new): `build_edit_proposal`, `should_auto_approve_edit`, sensitive-path guards, ACP requester wiring
- `acp_adapter/server.py`: `SessionModeState` advertised on new/load/resume/fork; `set_session_mode` drives policy; `set_config_option` keeps backwards-compat for the legacy `edit_approval_policy` id
- `acp_adapter/events.py`: `make_tool_progress_cb` accepts `edit_approval_policy_getter` and pre-computes the diff for auto-approved edits
- `acp_adapter/tools.py`: `build_tool_start` shows the structured diff on the tool card when an edit will be auto-approved
- `model_tools.py`: ACP edit-approval guard around `write_file` / `patch`
- Tests: `tests/acp/test_edit_approval.py`, `test_server.py`, `test_tools.py`, `test_mcp_e2e.py`

## Validation
| | Before | After |
|---|---|---|
| ACP suite (tests/acp/) | 258 passed | 258 passed |
| Architectural fit | edit-approval lives on `config_options` (hides Zed model picker) | edit-approval lives on `modes` (coexists with model picker) |
| Auto-approve diff visibility | none — auto-approved edits skip the approval card silently | diff rendered on tool-start card |

Original PR: #27034
 (subset)