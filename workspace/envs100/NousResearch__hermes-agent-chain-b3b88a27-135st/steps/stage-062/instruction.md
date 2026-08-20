**feat(auxiliary): default 'auto' routing to main model for all users**

## Summary
Changes the auxiliary-client `auto` policy so every user — including aggregator users (OpenRouter, Nous Portal) — gets their **main chat model** for side tasks (compression, vision, web extraction, session search, approval, MCP, title generation, flush memories, skills hub) by default.

 (which added the UI to configure these per-task).

## Before
```
Main provider = OpenRouter, Main model = anthropic/claude-sonnet-4.6
  → Context compression runs on google/gemini-3-flash-preview (provider default)
  → Vision runs on google/gemini-3-flash-preview
  → Session search, title gen, etc. run on gemini-flash

Main provider = DeepSeek, Main model = deepseek-chat
  → All aux tasks run on deepseek-chat (non-aggregator path already did this)
```
Behavior was inconsistent and surprising — users picked Claude / GPT / their preferred model, but side tasks silently ran on Gemini Flash.

## After
```
Every user's main provider + main model is the primary aux backend.
Fallback chain (OpenRouter → Nous → custom → Codex → API-key providers)
runs ONLY when the main provider has no working client.
Explicit per-task overrides in config.yaml still win.
```

## Changes
- **`agent/auxiliary_client.py`**
  - `_resolve_auto()`: dropped the `main_provider not in _AGGREGATOR_PROVIDERS` guard. All users take Step 1 now.
  - `resolve_vision_provider_client()` auto path: unified aggregator + exotic provider branches. Everyone goes through `resolve_provider_client(main_provider, main_model)`, with `_PROVIDER_VISION_MODELS` overrides preserved for xiaomi (mimo-v2-omni), zai (glm-5v-turbo).
  - Removed dead `_AGGREGATOR_PROVIDERS` constant (its only use was the guard we just removed).
  - Updated docstrings.
- **`hermes_cli/main.py`**
  - Aux-config menu header copy updated to reflect new semantics: "'auto' means 'use my main model' — Hermes only falls back to a lightweight backend if the main model is unavailable."
- **`tests/agent/test_auxiliary_main_first.py`** — 12 regression tests:
  - OpenRouter main → aux uses main model (not Gemini Flash)
  - Nous main → aux uses main model (not free-tier MiMo)
  - DeepSeek main → unchanged (sanity check)
  - Runtime kwarg override wins over config
  - Main unavailable → chain activates
  - Vision: OpenRouter/Nous main → main model used
  - Vision: `_PROVIDER_VISION_MODELS` override (xiaomi → mimo-v2-omni) preserved
  - Vision: explicit config override still bypasses auto path
  - Constant-removal guard

## Cost note
This increases cost for aggregator users who had cheap aux tasks before. Context compression and session search are the biggest items. Any user who wants the old cheap-aux behavior can pin specific tasks to a cheap model via `hermes model → Configure auxiliary models...` (PR #11891).

## Validation
| | Result |
|---|---|
| `tests/agent/test_auxiliary_main_first.py` (new) | 12 / 12 pass |
| `tests/agent/test_auxiliary_client.py` (regression) | all pass |
| `tests/agent/test_auxiliary_named_custom_providers.py` | all pass |
| `tests/agent/test_vision_resolved_args.py` | all pass |
| `tests/agent/test_title_generator.py` + compress_focus + compressor_fallback_update | all pass |
| `tests/hermes_cli/test_aux_config.py` (#11891 UI) | all pass |
| Live PTY smoke — new menu copy renders | OK |
| 119 targeted tests total | 119 / 119 pass |

Pre-existing failures on main (subagent_progress, model_validation, cmd_update) are inherited — not caused by this PR.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_auxiliary_main_first.py`