**fix(kanban): ignore stale HERMES_KANBAN_BOARD for removed boards**

Salvages #23900 by @QuenVix.

fixes stale HERMES_KANBAN_BOARD env not checked against board_exists; current main returns env value unconditionally; 23 LOC focused fix

Cherry-picked onto current main with original authorship preserved via rebase merge.