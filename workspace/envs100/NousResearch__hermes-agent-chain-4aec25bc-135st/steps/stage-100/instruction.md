**fix: assign single-task kanban decompositions**

Salvages #28227 by @DoGMaTiiC.

Single-task decompose path currently calls specify_triage_task without assignee; PR threads assignee through specify_triage_task. 165 LOC, targeted.

Cherry-picked onto current main with original authorship preserved via rebase merge.