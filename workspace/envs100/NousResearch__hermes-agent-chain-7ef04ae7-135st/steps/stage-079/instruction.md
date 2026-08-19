**fix(delegate): route subagent progress lines through _safe_print for ACP stdio**

## Summary

`delegate_task` progress lines now stay off stdout in headless JSON-RPC stdio hosts (ACP, gateway API), so subagent fan-out no longer corrupts the protocol frame stream.

Root cause: the per-task completion display (`✓ [1/3] Research done (17.92s)`) was emitted via a bare `print()` whenever no CLI spinner was attached. Under ACP — where `AIAgent` routes human output to stderr via a custom `_print_fn` — that landed on **stdout** and broke JSON-RPC framing, surfacing in the adapter as `Failed to parse JSON message: ✓ [3/3] … SyntaxError`.

## Changes

- `tools/delegate_tool.py`: add `_emit_parent_console(parent_agent, line)` — prefers `parent_agent._safe_print` (the same hook `AIAgent` uses for every other user-facing print), falls back to `print()` only when no router is wired up or it raises. Swap the two completion-line `print()` sites to use it.
- `tests/tools/test_delegate_toolset_scope.py`: 4 new tests covering `_safe_print` routing, stdout fallback (no router), exception fallback, and non-callable guard.
- `scripts/release.py`: AUTHOR_MAP entry for the contributor.

## What was dropped

The original PR also added a preset-toolset-expansion fix (`_expand_parent_enabled_toolsets`). That symptom is **already fixed on current main** by the more general `_expand_parent_toolsets()` — verified E2E: a `hermes-acp` parent intersected against LLM-requested `["browser","terminal","web"]` already yields the correct non-empty set. Adding the PR's helper would have been redundant, so only the stdio-safe printing fix is salvaged.

## Validation

| | Before | After |
|---|---|---|
| Progress line under ACP | hits stdout, corrupts JSON-RPC | routed to `_safe_print` → stderr |
| CLI (no `_print_fn`) | `print()` | `print()` (unchanged) |
| `_safe_print` raises | n/a | falls back to `print()` |
| Tests | 5 | 9/9 pass (4 new) |

Salvaged from #14180 by @theAgenticBuilder — preset-expansion already on main, stdio-safe print fix preserved with authorship.

## Infographic

![delegate_task stdio-safe progress printing](https://v3b.fal.media/files/b/0aa05ba1/PXacalWUWMIHsrMQYpFX9_IMZuINvv.png)