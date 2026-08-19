**fix(kanban): reset failure counters on unblock_task**

Salvages #24022 by @bradhallett.

Resets consecutive_failures/last_failure_error in unblock_task UPDATE; confirmed missing in main (unblock_task only flips status). Small, well-isolated bug fix.

Cherry-picked onto current main with original authorship preserved via rebase merge.