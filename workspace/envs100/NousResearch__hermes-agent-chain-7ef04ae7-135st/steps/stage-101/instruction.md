**fix(terminal): prevent corrupted session snapshots during init**

## Summary
Terminal commands no longer intermittently return exit 127 after session init. The init snapshot's function dump used a line-based filter that tore function bodies apart, corrupting the snapshot sourced before every command.

## Root Cause
`init_session` built the snapshot with:

```
declare -f | grep -vE '^_[^_]'
```

That filter is **line-based**: it removes a function's *header* line (e.g. `_foo () `) but leaves the orphaned `{ … }` body behind. When the snapshot is sourced before each command, the leftover body executes/syntax-errors, polluting the shell — surfacing as intermittent exit 127.

## Changes
- `tools/environments/base.py`: filter private (`_`-prefixed) functions **by name** via `declare -F`, then dump only those whole definitions with `declare -f <names>` — a body is never torn. Guards against an empty name list (bare `declare -f` would otherwise dump every function, leaking the private ones we meant to drop).
- `tools/environments/base.py`: treat a non-zero bootstrap exit code as snapshot-init failure, so execution falls back to login-shell-per-command mode.
- `tests/tools/test_base_environment.py`: regression test asserting `snapshot_ready` stays false when bootstrap exits non-zero.
- Preserves the atomic-write (`$BASHPID` temp + `mv -f`) machinery from #38249.

## Validation
| | Before | After |
|---|---|---|
| `_foo` private function in snapshot | header stripped, body orphaned (corrupt) | dropped whole, no torn body |
| Only-private-funcs edge case | n/a | guarded — no leak, no corruption |
| Non-zero bootstrap exit | `snapshot_ready=True` anyway | falls back to `bash -l` |
| Targeted tests | — | 26/26 pass |
| Live `LocalEnvironment` E2E | — | snapshot sources cleanly (rc=0), real commands return correct exit codes |

Salvaged from #10169 by @etherman-os — authorship preserved.

## Infographic

![terminal-snapshot-corruption-fixed](https://v3b.fal.media/files/b/0aa06d43/7D9RwyrHRcFOOyMvEG7z9_Imo4KCdb.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_base_environment.py`