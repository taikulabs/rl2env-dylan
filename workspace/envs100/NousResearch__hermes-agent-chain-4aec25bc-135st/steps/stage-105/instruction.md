**feat(kanban): add --sort option to 'hermes kanban list'**

Salvages #25745 by @LizerAIDev.

Adds `--sort {created|created-desc|priority|priority-desc|status|assignee|title|updated}` to `hermes kanban list`. Validated against `VALID_SORT_ORDERS` map; invalid values raise `ValueError`. Default behaviour (priority DESC, created ASC) is unchanged when `--sort` is omitted.

Original branch was stale; applied substantive feature manually onto current main. Authorship preserved via rebase merge.

## Validation
- New test_list_tasks_order_by passes.