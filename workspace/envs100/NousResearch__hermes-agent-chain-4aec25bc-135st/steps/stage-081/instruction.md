**fix(kanban): clear _INITIALIZED_PATHS in remove_board so recycled DBs re-init schema**

Salvages #23852 by @briandevans.

Bug fix: remove_board doesn't discard _INITIALIZED_PATHS in main; confirmed missing. 36-LOC targeted fix + test.

Cherry-picked onto current main with original authorship preserved via rebase merge.