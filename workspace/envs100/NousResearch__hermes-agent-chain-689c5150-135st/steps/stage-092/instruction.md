**fix(send_message): URL-encode Matrix room IDs and add Matrix to schema examples**

## Summary
Two fixes for Matrix in the `send_message` tool:

**1. URL-encode room IDs in the API path**
Matrix room IDs (`!abc:server`) contain `!` and `:` which must be percent-encoded when used in URI path segments per the Matrix C-S spec. Without this, some homeservers reject the PUT request. Now uses `urllib.parse.quote(chat_id, safe="")`.

**2. Add Matrix examples to the tool schema**
The `target` description now includes `'matrix:!roomid:server.org'` and `'matrix:@user:server.org'` so models know the correct format for Matrix targets.

## What changed
- `tools/send_message_tool.py`: URL-encode room ID in `_send_matrix()`, add Matrix to schema examples
- `tests/tools/test_send_message_tool.py`: 1 test verifying percent-encoding in the PUT URL

## Context
Third in a series of Matrix sending fixes:
- PR #10114: messaging toolset registration (merged)
- PR #10117: _parse_target_ref Matrix handling (merged)
- This PR: URL encoding + schema