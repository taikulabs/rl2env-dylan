**fix(daytona): migrate sandbox lookup from find_one to get/list**

## What does this PR do?

Migrates Daytona sandbox lookup from the deprecated (removed in the latest Daytona version) `find_one(labels=...)` API to `get(name)` with a deterministic sandbox name (`hermes-{task_id}`).

Includes a legacy fallback via `list(labels=...)` so sandboxes created before this migration are still resumable.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_daytona_environment.py`