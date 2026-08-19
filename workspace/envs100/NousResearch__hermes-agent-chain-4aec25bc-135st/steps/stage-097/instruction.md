**fix(kanban): avoid unsafe Windows worker Hermes shim resolution**

Salvages #27483 by @hanzckernel.

Hardens _resolve_hermes_argv against Windows .cmd/.bat shims, absolutizes HERMES_BIN, skips '.' PATH entry. Main has a 30-line version; this adds Windows-specific safety + tests.

Cherry-picked onto current main with original authorship preserved via rebase merge.