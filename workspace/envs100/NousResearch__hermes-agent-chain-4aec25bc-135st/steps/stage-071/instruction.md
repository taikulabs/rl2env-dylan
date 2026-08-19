**feat(acp): enrich Zed permission cards (command in title + reject_always)**

Salvage of #26625 by @HenkDz cherry-picked onto current main.

## Summary
Before: dangerous-command approval cards in Zed showed only the description in the card title, with the actual command relegated to the body. Easy to miss in the compact card header. Now the command is in the title, the body shows description + `$ command`, and the structured `raw_input` carries both for clients that consume the schema. Also adds a `reject_always` option using the standard ACP `PermissionOptionKind` literal (not Zed-special).

## Changes
- `acp_adapter/permissions.py`: card title = "{description}: {command}", body = `{description}\n$ {command}` as a text_block, structured raw_input, optional deny_always option behind an SDK feature probe (graceful degradation on older ACP SDKs)
- `tests/acp/test_permissions.py`: 6 new tests covering title/body composition, option list with/without allow_permanent, deny_always outcome mapping, and the reject_always kind

## Validation
`scripts/run_tests.sh tests/acp/test_permissions.py` → 9/9 passing.

 (salvage merge — author preserved).