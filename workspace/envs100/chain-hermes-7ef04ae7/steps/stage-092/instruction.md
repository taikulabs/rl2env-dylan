**feat(journey): edit and delete learned skills/memories**

<img width="1898" height="1408" alt="image" src="https://github.com/user-attachments/assets/1c5e4fb7-406b-4ab0-b975-0da0612ca760" />

## Summary
Edit and delete journey nodes (learned skills + memories) across all surfaces, building on the merged `/journey` timeline.

- **Backend** — `agent/learning_mutations.py` maps node ids → on-disk SKILL.md or §-delimited memory chunks; skill deletes archive (curator-restorable), memory deletes rewrite `MEMORY.md`/`USER.md`
- **CLI** — `hermes journey list|delete|edit <id>` with confirm prompt + `$EDITOR`
- **TUI** — `/journey` overlay: `d` delete (y confirm), `e` edit (`$EDITOR` via shared `openInEditor` helper), live refresh
- **Desktop** — right-click context menu on star-map nodes: inline edit modal, delete confirm, graph reloads on mutation

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_learning_mutations.py`