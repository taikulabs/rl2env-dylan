**fix(mcp): combine content and structuredContent when both present**

## Summary

When an MCP server returns both `content` (model-oriented text) and `structuredContent` (machine-oriented JSON metadata), the MCP client now combines them instead of discarding `content`.

**Before:** `structuredContent` took full precedence — the agent only saw the structured JSON and lost the text content entirely.

**After:**
- Both present → `{"result": <text>, "structuredContent": <json>}`
- Only structured → `{"result": <json>}` (unchanged)
- Only text → `{"result": <text>}` (unchanged)

**Real-world impact:** Desktop Commander MCP's `read_file` returns file text in `content` and metadata (`{fileName, filePath, fileType}`) in `structuredContent`. Previously, the agent would only see the metadata and miss the actual file contents.

**MCP spec alignment:** SEP-1624 recommends that conversational/agent clients prefer `content` (model-oriented). Our previous behavior preferred `structuredContent` (machine-oriented), which is intended for programmatic/code UX.

## Changes
- `tools/mcp_tool.py`: Combine both fields when present; `content` as primary, `structuredContent` as supplement
- `tests/tools/test_mcp_structured_content.py`: Updated existing test + added Desktop Commander scenario test

## Test Results
- 5/5 structured content tests pass
- 163/163 MCP tool tests pass

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_mcp_structured_content.py`