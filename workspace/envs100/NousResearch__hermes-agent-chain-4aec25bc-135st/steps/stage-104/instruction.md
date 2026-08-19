**feat(kanban): add max_in_progress config to cap concurrent running tasks**

Salvages #22981 by @SimbaKingjoe.

Adds `kanban.max_in_progress` config knob — caps simultaneously running tasks. When the board already has N running, dispatcher skips spawning more so slow workers (local LLMs, resource-constrained hosts) finish what they have before more pile up and time out.

- New `max_in_progress` kwarg on `dispatch_once()`
- Gateway dispatcher reads `kanban.max_in_progress` from config with validation (warns on invalid/below-1 values)
- 3 new tests covering at-limit / partial-headroom / unlimited paths

Original branch was stale; applied substantive change manually onto current main. Authorship preserved via rebase merge.