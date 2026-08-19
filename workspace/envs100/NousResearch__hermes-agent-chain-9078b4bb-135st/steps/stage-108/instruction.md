**fix(config): write config.yaml as UTF-8 to stop emoji/personality corruption**

## Summary
Config is written as readable UTF-8 again, so the shipped personalities (emoji/kaomoji) no longer corrupt `config.yaml` on write.

**Root cause:** `utils.atomic_yaml_write` — the canonical config writer used by config/auth/gateway/onboarding — called `yaml.dump()` without `allow_unicode=True`. The default personalities in `cli.py` (`kawaii`/`catgirl`/`surfer`/`hype`) contain emoji + kaomoji, so PyYAML emitted astral-plane chars as 8-digit `\UXXXXXXXX` escapes inside multi-line double-quoted strings wrapped with `\` line-continuations. Stricter/non-PyYAML parsers, editors, and hand-edits break that structure into unclosed quotes → the whole config fails to parse → silent fallback to defaults → `custom_providers` (e.g. `custom:llmbase`) silently ignored. .

## Changes
- `utils.py`: `atomic_yaml_write` now passes `allow_unicode=True`.
- `tui_gateway/server.py`: config writer gets `allow_unicode=True` (same bug class).
- `plugins/platforms/telegram/adapter.py`: its atomic config write gets `allow_unicode=True` (same bug class).
- `tests/hermes_cli/test_atomic_yaml_write.py`: regression test — round-trips the default personalities + skin cursor, asserts no `\U`/`\u` escapes and a clean reload.

(`hermes_cli/xai_retirement.py` uses ruamel.yaml, which defaults to unicode — unaffected.)

## Validation
| | Before | After |
|---|---|---|
| emoji on disk | `\U0001F525` in folded `"..."` | `🔥` verbatim |
| config reparse | breaks in strict parsers / hand-edits | clean |
| `custom_providers` after rewrite | lost (fallback to defaults) | survives |

E2E: ran the real `save_config`/`load_config` path against a temp `HERMES_HOME` with the actual default personalities + a `custom:llmbase` entry — no `\U`, parses clean, providers survive. New regression test + 136 existing config/auth/persistence tests pass.

## Infographic

![CONFIG WRITER: UTF-8 ENFORCED](https://v3b.fal.media/files/b/0a9f89df/rXCNnimr1MAM_oP7lGsEM_auyc5YXo.png)