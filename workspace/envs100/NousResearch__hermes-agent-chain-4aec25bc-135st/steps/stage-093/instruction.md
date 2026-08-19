**fix(kanban): persist worker session metadata on completion**

Salvages #25579 by @wesleysimplicio.

Stamps task_runs.metadata.worker_session_id from HERMES_SESSION_ID on kanban_complete. Targets tools/kanban_tools.py.

Cherry-picked the substantive commit (skipping the AUTHOR_MAP-fixup tip) onto current main with original authorship preserved via rebase merge.