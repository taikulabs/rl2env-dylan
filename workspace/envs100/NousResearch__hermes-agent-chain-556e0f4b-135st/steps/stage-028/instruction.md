**fix(banner): normalize toolset labels and use skin colors**

Two fixes for the CLI welcome banner:

1. **Toolset name normalization** — strips `_tools` suffix from internal identifiers (`web_tools` → `web`, `homeassistant_tools` → `homeassistant`) and stops appending `_tools` to unavailable toolsets.

2. **Skin color compliance** — replaces 6 hardcoded hex colors in toolset rows, overflow line, and MCP server section with the `dim`/`accent`/`text` skin variables already resolved at the top of the function. Custom skins now actually apply to these elements.

Salvaged from PR #1871 by @kshitijk4poor. 4 tests added.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_banner.py`