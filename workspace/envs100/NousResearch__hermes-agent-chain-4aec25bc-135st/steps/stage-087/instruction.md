**fix(kanban): promote blocked tasks when parent dependencies complete**

Salvages #24018 by @bradhallett.

recompute_ready in main still scans only 'todo' rows; PR extends to 'blocked' with parent-done check and resets failure counters.

Cherry-picked onto current main with original authorship preserved via rebase merge.