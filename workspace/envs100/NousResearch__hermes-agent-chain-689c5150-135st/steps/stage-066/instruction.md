**fix: make tool registry reads thread-safe**

## Summary

Adds thread safety to `ToolRegistry` — the process-global singleton in `tools/registry.py`. MCP dynamic discovery can register/deregister tools at runtime from async callbacks while the main thread iterates registry dicts.

## Changes

- Serialize `register()` and `deregister()` with an internal `RLock`
- Build multi-step registry answers from coherent snapshots (copy under lock, work outside lock)
- Add public accessors (`get_entry()`, `get_registered_toolset_names()`, `get_tool_names_for_toolset()`) replacing direct `registry._tools` access
- Switch `toolsets.py` and `hermes_cli/plugins.py` off private `_tools` access
- Focused regression tests for concurrent register/deregister and plugin toolset resolution