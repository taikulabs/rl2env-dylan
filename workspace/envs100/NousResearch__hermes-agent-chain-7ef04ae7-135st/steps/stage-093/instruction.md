**fix(journey): atomic memory writes + desktop lint fixups ()**

Fast-follow to #55859 (merged). Three small, independent fixes surfaced in review.

## Summary
- **fix** — `#55859` left two `perfectionist` sort violations in `apps/desktop/.../star-map.tsx` (the `NodeContextMenu` import + the canvas `onContextMenu` prop), failing `npm run lint` in the desktop workspace. Reordered both.
- **refactor** — `agent/learning_mutations.py` had re-implemented the `§`-delimited read/write that `tools/memory_tool` already owns, and its writer used a plain `write_text` (truncate-then-write), reintroducing the partial-file race that `MemoryStore._write_file` deliberately avoids with atomic temp-file + rename. Now routes both reads and writes through `MemoryStore._read_file`/`_write_file` — atomic against concurrent readers, single-sourced format, indices still aligned with the graph.
- **test** — locks format-parity: a journey edit leaves `MEMORY.md` byte-identical to `MemoryStore`'s own `§`-join and round-trips through `_read_file`, so the two surfaces can't drift.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_learning_mutations.py`