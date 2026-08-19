**fix(security): operator opt-in for plugin tool_override (sink-enforced) + enable-time consent**

## Summary

A plugin can no longer silently replace a built-in tool: enabling a non-bundled plugin now requires an explicit operator decision about the privileged `tool_override` capability, and the registry enforces that grant at the point of registration.

Salvage of #29249 (@memosr) — the sink-level opt-in gate, rebased onto current `main` — plus an enable-time consent layer on top so the operator makes the call when they enable the plugin instead of discovering a config key after a runtime rejection.

Root cause: `tool_override` let any enabled plugin call `register(override=True)` to replace a built-in (`shell_exec`, `write_file`, `web_fetch`, …) with only a DEBUG log line as a trace. No trust gate, despite the codebase already gating the equivalent `ctx.llm` provider override behind `allow_provider_override`.

## Changes

- `tools/registry.py`: enforce the override opt-in at the registration sink. Authorization is bound to the handler's **defining plugin module** (`handler.__globals__["__name__"]`), captured at load and never cleared — so direct `registry.register(override=True)`, threaded, and delayed-callback paths are all gated identically. Built-in/MCP handlers live outside the plugin namespace and are unaffected. *(@memosr)*
- `hermes_cli/plugins.py`: `PluginContext.register_tool(override=True)` checks `plugins.entries.<id>.allow_tool_override`; bundled plugins exempt; fail-closed on config load failure. *(@memosr)*
- `hermes_cli/plugins_cmd.py` + `hermes_cli/subcommands/plugins.py`: enable-time consent. `hermes plugins enable <non-bundled>` prompts *"Allow this plugin to replace built-in tools?"* with a **deny default** (blank Enter / non-interactive stdin / EOF all fail closed). `--allow-tool-override` / `--no-allow-tool-override` flags for scripted and headless use. Bundled plugins are never prompted and never get an entry written. The choice is persisted under the same `plugins.entries.<key>.allow_tool_override` key the sink reads (`manifest.key` == discovery key), so consent and enforcement compose end to end.

## Validation

| Scenario | Result |
|---|---|
| Enable + grant → plugin override at load | sink **permits** (override takes effect) |
| Enable + decline → plugin override at load | sink **rejects** (built-in survives) |
| Blank Enter / EOF / piped stdin | fail closed → deny |
| Bundled plugin enable | no prompt, no entry written |
| `--allow-tool-override` full argparse path | writes the grant, override permitted |
| Direct registry import bypass | rejected at sink |
| Delayed/threaded override callback | rejected at sink |

- E2E verified against an isolated `HERMES_HOME` with real plugin load and real config I/O (all rows above).
- Tests: 116/116 pass across `tests/hermes_cli/test_plugins.py` and `tests/hermes_cli/test_plugins_cmd_enable_disable_nested.py` — @memosr's 3 sink-gate regression tests (direct-import + delayed-callback bypass) plus 6 new consent tests. ruff clean.

## Infographic

![Plugin tool-override: consent + enforcement](https://v3b.fal.media/files/b/0aa05cb4/VEMCmNd2Gz3mrLY_qg4f7_EMmoMhru.png)

---

Salvaged from #29249 — @memosr's commits cherry-picked with authorship preserved; consent layer added on top.