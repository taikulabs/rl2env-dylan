**fix(kanban): align board_exists with board discovery rules**

Salvages #24086 by @soynchux.

board_exists alignment still applies — main still uses `d.is_dir() or` fallthrough (18 LOC).

Cherry-picked onto current main with original authorship preserved via rebase merge.