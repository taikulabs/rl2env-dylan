**fix: cap percentage displays at 100% in stats, gateway, and memory tool**

Salvage of PR #3533 (binhnt92).

Follow-up to PR #3480 which capped `display.py` but missed 5 other unclamped percentage sites. When token counts overshoot context length (before compression fires), users see >100% in `/stats` output, gateway status, and memory tool headers.

### Changes

Applies `min(100, ...)` at all 5 remaining sites:

| File | Function | Context |
|------|----------|---------|
| `agent/context_compressor.py` | `get_status()` | `usage_percent` field |
| `cli.py` | `_show_usage()` | `/stats` command |
| `gateway/run.py` | `_handle_usage_command()` | Gateway `/stats` handler |
| `tools/memory_tool.py` | `_success_response()` | Memory usage display |
| `tools/memory_tool.py` | `_render_block()` | Memory header display |

### Tests

15 tests in `tests/test_percentage_clamp.py`:
- Integration test on `ContextCompressor.get_status()` with overshoot
- Formula tests for CLI, gateway, and memory tool calculations
- Source-line verification that `min(100,` exists in all 4 files

Live verified: all overshoot scenarios return 100%, normal percentages unaffected.