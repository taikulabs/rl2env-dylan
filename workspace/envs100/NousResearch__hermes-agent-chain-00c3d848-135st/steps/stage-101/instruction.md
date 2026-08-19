**feat(fast): broaden /fast whitelist to all OpenAI + Anthropic models**

## Summary
`/fast` now works on every OpenAI flagship (`gpt-*`, `o1*`, `o3*`, `o4*`) and every Claude model (`claude-*`), including future releases like `gpt-5.5` that weren't in the hardcoded frozenset.

Previously `_PRIORITY_PROCESSING_MODELS` was a frozenset of 13 specific slugs — any post-catalog model (gpt-5.5, gpt-5.5-mini, …) silently skipped Priority Processing. Same shape on Anthropic: only Opus 4.6 was listed, so Sonnet / Haiku / Opus 4.7 were all unsupported.

## Changes
- `hermes_cli/models.py`: replaced both frozensets with `_OPENAI_FAST_MODE_PREFIXES` tuple + `_is_openai_fast_model()`, and a `claude-` prefix check in `_is_anthropic_fast_model()`. `resolve_fast_mode_overrides()` still routes OpenAI → `service_tier=priority`, Anthropic → `speed=fast`.
- `tests/cli/test_fast_command.py`: updated tests that asserted narrow sets, added `test_all_anthropic_models_supported`, `test_codex_models_excluded`, `test_non_claude_models_not_anthropic_fast`.

## Safety nets preserved
- Codex-series (`*codex*`) stays excluded — they route through the Codex Responses API which doesn't accept `service_tier`.
- `agent/anthropic_adapter.py` already gates `speed=fast` on native Anthropic endpoints via `_is_third_party_anthropic_endpoint`, so Claude models on OpenRouter / Bedrock / opencode-zen won't leak the unknown beta header.
- `service_tier=priority` is silently dropped by non-OpenAI proxies, so false positives are harmless.

## Validation
| | Before | After |
|---|---|---|
| `gpt-5.5` supports /fast | No | Yes |
| `claude-sonnet-4.6` supports /fast | No | Yes |
| `gpt-5.3-codex` supports /fast | No | No (codex excluded) |
| `gemini-3-pro` supports /fast | No | No |

33/33 in `tests/cli/test_fast_command.py`. Full `tests/hermes_cli/` suite: 3025 pass, 2 pre-existing unrelated failures (cmd_update TUI node deps, web_server schema).