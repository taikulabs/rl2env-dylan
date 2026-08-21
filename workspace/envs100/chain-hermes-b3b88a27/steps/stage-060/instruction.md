**feat(hermes model): add Configure auxiliary models UI**

## Summary
Users can now configure per-task auxiliary models (vision, compression, web extract, etc.) from `hermes model` instead of hand-editing `config.yaml`.

## UI flow
`hermes model` now has two new bottom entries:

    ...
    Custom endpoint (enter URL manually)
    Configure auxiliary models...
    Leave unchanged         ← renamed from 'Cancel'

Clicking "Configure auxiliary models..." → task picker with current settings inline:

    Auxiliary models — side-task routing

    Hermes uses small, fast models for vision, compression, web
    extraction, and other side tasks. "auto" lets Hermes pick the
    best available backend automatically (OpenRouter → Nous Portal
    → your main provider). You rarely need to change these —
    override only if you want a specific model for a task.

    Vision            (image/screenshot analysis)  auto
    Compression       (context summarization)      auto
    Web extract       (web page summarization)     auto
    Session search    (past-conversation recall)   auto
    Approval          (smart command approval)     auto
    MCP               (MCP tool reasoning)         auto
    Flush memories    (memory consolidation)       auto
    Title generation  (session titles)             auto
    Skills hub        (skills search/install)      auto
    Reset all to auto
    Back

Clicking a task → provider picker scoped to already-authenticated providers (reuses `list_authenticated_providers()`) → model picker with live pricing. Saves to `auxiliary.<task>.provider` / `model` / `base_url` / `api_key`; the main model config is never touched.

## Changes
- `hermes_cli/main.py` — new `_aux_config_menu`, `_aux_select_for_task`, `_aux_flow_provider_model`, `_aux_flow_custom_endpoint`, `_save_aux_choice`, `_reset_aux_to_auto`, `_format_aux_current`; dispatch wired into `select_provider_and_model`
- `hermes_cli/config.py` — add `title_generation` task to `DEFAULT_CONFIG.auxiliary` (was called from `agent/title_generator.py` but missing from defaults, so config-backed timeout overrides never worked for that task)
- `tests/hermes_cli/test_aux_config.py` — 20 new tests covering save/reset/format + menu dispatch

## Design notes
- The aux picker does NOT re-run credential/OAuth setup. Users authenticate providers through the normal `hermes model` flow, then route aux tasks to them here. Avoids duplicating the 13-function `_model_flow_*` dispatch tree.
- `_reset_aux_to_auto` only clears routing fields (`provider`/`model`/`base_url`/`api_key`); user-tuned `timeout` / `download_timeout` values are preserved.
- "Cancel" sentinel string preserved internally — only the display label changed to "Leave unchanged", so existing dispatch (`ordered[provider_idx][0] == "cancel"`) still works.

## Validation
| | Result |
|---|---|
| `tests/hermes_cli/test_aux_config.py` (new) | 20 / 20 pass |
| `tests/hermes_cli/` (regression) | 2224 / 2224 pass |
| `tests/agent/` auxiliary client + title gen + compression | 72 / 72 pass |
| Live PTY smoke — menus render, dispatch works | OK |
| Main model config unchanged after aux save (E2E) | OK |
| Timeouts preserved across save + reset (E2E) | OK |

## Follow-up
A separate PR will change `auto` resolution to prefer the main model for every aux task (instead of falling through to cheap aggregator defaults), and update the aux menu copy accordingly.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_aux_config.py`