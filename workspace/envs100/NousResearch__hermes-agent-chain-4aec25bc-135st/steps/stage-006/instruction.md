**feat(plugins): tool override flag for replacing built-in tools ()**

## Summary
Plugins can now replace a built-in tool by passing `override=True` to `ctx.register_tool()`. .

## Changes
- `tools/registry.py`: `register()` gets `override: bool = False`. When set, shadowing logs at INFO instead of rejecting. Default behavior unchanged — accidental shadows still rejected with an error pointing at the flag.
- `hermes_cli/plugins.py`: `PluginContext.register_tool()` forwards `override`.
- `tests/hermes_cli/test_plugins.py`: three new tests (rejects without flag, replaces with flag, no-op on brand-new names).
- `website/docs/guides/build-a-hermes-plugin.md`: new "Overriding a built-in tool" subsection.

## Validation
| | Status |
|---|---|
| Targeted (plugins + registry + mcp + model_tools) | 137/137 |
| E2E (real plugin overriding `web_search` end-to-end) | handler swap confirmed via `registry._tools["web_search"].handler({"query": ...})` |

## Why this and not a `~/.hermes/custom_tools/` directory
The original issue proposed a parallel discovery system. We already have a plugin discovery system that registers tools via `ctx.register_tool()` — the only thing missing was override semantics. Adding a flag is ~20 LOC versus ~160 for a parallel loader, doesn't violate extend-don't-duplicate, and composes with the existing `pre_tool_call` hook so users get both wholesale replacement AND runtime interception from one extension surface.

iRonin originally promised a PR on `ironin/tool-override-plugin` but never pushed the branch (404). This PR delivers the user-facing capability they asked for.