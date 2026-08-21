**fix(file): anchor device symlink guard to task cwd (dropped commit from #34466)**

## Summary
Picks up the second commit of PR #34466 that was dropped during the #50221 salvage. The `read_file` device guard now anchors relative device-path checks to the task cwd before the symlink-hop walk, closing a residual bypass that the first commit (already on main) left open.

## Root cause
#50221 `, announced in a PR comment, not the body) that I missed. That follow-up fixes the case where the symlink-hop walk interpreted a **relative** workspace symlink against the Python process cwd instead of the task cwd — so a relative symlink to `/dev/../dev/stdin` in a session where `TERMINAL_CWD` is the workspace would miss the blocked device target before `read_file`'s own task-cwd resolution.

## Changes
- `tools/file_tools.py`: `_is_blocked_device(filepath, base_dir=None)` joins relative paths to `base_dir` before normpath; `read_file_tool` passes `_resolve_base_dir(task_id)` for non-absolute inputs. Absolute paths and the final realpath fallback unchanged.
- `tests/tools/test_file_read_guards.py`: regression test for a task-cwd-relative device-alias symlink with process cwd != task cwd.

## Validation
| | Before (main) | After |
|---|---|---|
| relative `/dev/../dev/stdin` symlink, `TERMINAL_CWD`=workspace, process cwd elsewhere | guard misses target | BLOCKED |
| `tests/tools/test_file_read_guards.py` | 41 passed | 42 passed |

E2E: built the exact bypass (workspace symlink → `/dev/../dev/stdin`, chdir to a different process cwd, `TERMINAL_CWD` set) and confirmed `read_file_tool` returns "device file" and never reaches the read sink.

Picks up the dropped commit from PR #34466 by @egilewski. , #29158.

## Infographic
![read_file device guard task-cwd anchor](https://v3b.fal.media/files/b/0a9f3862/YqfPvtqdNn6vYqB2BkDT-_ANub4QYr.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_file_read_guards.py`