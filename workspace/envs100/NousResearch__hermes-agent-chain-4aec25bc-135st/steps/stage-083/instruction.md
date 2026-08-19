**fix(kanban): ignore `--board` override for `boards` subcommands**

Salvages #23924 by @QuenVix.

Two-line dispatcher reordering so 'boards' subcommands run before --board override; not landed in main and clearly correct.

Cherry-picked onto current main with original authorship preserved via rebase merge.