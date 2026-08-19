**fix(kanban): fingerprint crash errors to prevent fleet-wide retry exhaustion**

Salvages #24023 by @bradhallett.

Small crash-fingerprint grouping fix (96 LOC) — no fingerprint logic visible in main kanban_db.

Cherry-picked onto current main with original authorship preserved via rebase merge.