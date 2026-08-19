**fix(kanban): align failure diagnostics with retry limit**

Salvage of #25591 from @qWaitCrypto onto current main.

The dispatcher defaults `kanban.failure_limit: 2` (auto-block after 2 consecutive non-success attempts), but `kanban_diagnostics.py` defaulted `failure_threshold: 3` and the user-facing detail text mentioned a stale "default 5". Net effect: a task auto-blocks before the repeated-failure diagnostic ever fires.

- New `config_from_kanban_config()` translates runtime `kanban` config → diagnostics config.
- CLI + dashboard both pass the active kanban config to diagnostics.
- Default repeated-failure threshold derived from `kanban.failure_limit` unless `kanban.diagnostics.failure_threshold` (or legacy `spawn_failure_threshold`) is set explicitly.
- Diagnostic detail now reports the actual configured failure limit, not stale "default 5".

Aligned with the new auto-decompose path: failure_limit gates ALL kanban tasks regardless of how they got created, so auto-decomposed children inherit the same behavior.

Original PR: #25591.

## Validation
- All 35 `test_kanban_diagnostics.py` tests passing.