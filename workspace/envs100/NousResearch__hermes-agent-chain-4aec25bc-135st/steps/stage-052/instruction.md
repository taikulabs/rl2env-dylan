**fix(kanban): surface unusable triage auxiliary model (auto-decompose aware)**

Reworks @qWaitCrypto's #25640 idea to align with the auto-decompose dispatcher landed in #27572.

The original PR added a `triage_missing_specifier` diagnostic that always pointed at `auxiliary.triage_specifier`. After #27572, triage tasks fan out via `auxiliary.kanban_decomposer` (the primary path) and only fall back to `triage_specifier` when the LLM returns `fanout=false` — so the original wording would have steered users to configure the wrong slot when `kanban.auto_decompose` is on (the default).

## What this PR does

New diagnostic `triage_aux_unavailable` for tasks stuck in triage:

- `kanban.auto_decompose=True` (default): primary slot is `auxiliary.kanban_decomposer`, with `triage_specifier` mentioned as fan-out=false fallback.
- `kanban.auto_decompose=False`: primary slot is `auxiliary.triage_specifier`, with the manual `hermes kanban specify <id>` command surfaced as an action.

Default aux slots use `provider: auto` which falls back to the main model, so the rule only fires when both the explicit slot config AND the main-model auto fallback are absent. Quiet by default; informative when there's a real configuration gap.

Also adds `kd.config_from_runtime_config()` (extends #25591's `config_from_kanban_config` to also carry `auxiliary` + `model`) and switches CLI + dashboard call sites to use it. The old function is preserved for back-compat.

## Validation

- 45/45 `test_kanban_diagnostics.py` tests passing (35 existing + 10 new).
- Live E2E with isolated HERMES_HOME, real `load_config()`:
  - No main model + auto_decompose on → fires, points at `auxiliary.kanban_decomposer`.
  - Main model configured + aux defaults → silent (auto fallback works).
  - auto_decompose=False + no main model → fires, points at `auxiliary.triage_specifier` + offers manual `hermes kanban specify`.

Credit: @qWaitCrypto (co-authored). Original PR #25640 will be closed pointing at this.