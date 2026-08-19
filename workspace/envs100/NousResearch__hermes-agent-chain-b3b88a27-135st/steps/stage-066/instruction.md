**fix(file-ops): follow terminal env's live cwd instead of stale init-time cwd**

## Summary
`ShellFileOperations` captured the terminal env's cwd at `__init__` time and reused that stale value for every subsequent `_exec()`.  When the user ran `cd` via the terminal tool, `env.cwd` updated but `ops.cwd` did not.  Relative paths passed to `patch_replace` / `read_file` / `write_file` / `search` then targeted the ORIGINAL directory instead of the live one.

## Observed symptom
```
terminal:  cd .worktrees/my-branch
patch:     hermes_cli/main.py <old> <new>

Returns {"success": true} with a plausible unified diff.
But `git diff` in the worktree shows nothing.
The patch landed in the MAIN REPO's checkout of `main.py` instead.
```

Why it looked like a success: `patch_replace` computes the diff from the **in-memory** content vs new_content, not by re-reading the file. The write itself DID succeed — it just wrote to the wrong directory's copy of the same-named file.

Hit this personally while working on #11891 / #11900 — thought the patch tool was silently dropping writes on large files. It was not. It was writing to the right file path, in the wrong directory.

## Fix
`_exec()` now resolves cwd from live sources in order:

1. Explicit `cwd` arg (if the caller passed one)
2. Live `self.env.cwd` (tracks `cd` commands run via the terminal tool)
3. Init-time `self.cwd` (fallback for backends that don't track cwd)

`self.cwd` is kept as a last-resort fallback — it's safer to keep it than to break backends that don't expose a live `cwd` attribute.  The class docstring now explicitly documents the resolution policy and references the historical bug so future maintainers don't re-introduce the caching.

## Regression tests (`tests/tools/test_file_ops_cwd_tracking.py`)
5 new tests, all with a `_FakeEnv` that mirrors `BaseEnvironment`'s contract (cwd attribute + `execute(command, cwd=...)`):

| Test | What it guards |
|---|---|
| `test_exec_follows_env_cwd_after_cd` | `cd` in terminal → next `_exec` follows live cwd |
| `test_patch_replace_targets_live_cwd_not_init_cwd` | The exact reported bug |
| `test_explicit_cwd_arg_still_wins` | `cwd=` arg overrides env.cwd and self.cwd |
| `test_env_without_cwd_attribute_falls_back_to_self_cwd` | Backends without `cwd` still work |
| `test_patch_returns_success_only_when_file_actually_written` | patch success ↔ real file state |

## Validation
| | Result |
|---|---|
| `tests/tools/test_file_ops_cwd_tracking.py` (new) | 5 / 5 pass |
| `tests/tools/test_file_operations.py` (regression) | all pass |
| `tests/tools/test_patch_parser.py` (regression) | all pass |
| `tests/tools/` full dir (3195 pass, 9 pre-existing fails on main) | no new failures |
| Hand-written reproducer before/after fix | Confirms bug + fix |

The 9 failures in `tests/tools/` are pre-existing on main (test_delegate `_build_child_*` signature mismatches, test_registry builtin-set drift) — same set visible on PRs #11891 and #11900. Not caused by this PR.