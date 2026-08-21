**fix: normalize repeat<=0 to None — cron jobs deleted after first run when LLM passes -1**

## Root Cause

`mark_job_run()` checked `completed >= times` without guarding against negative values. When an LLM passes `repeat=-1` (a conventional infinite sentinel common in most APIs), the check `1 >= -1` evaluated to `True` and deleted the job after its first run.

## Changes

**`cron/jobs.py` — `create_job()`**: normalize `repeat <= 0` to `None` before storing

```python
# Normalize repeat: treat 0 or negative values as None (infinite)
if repeat is not None and repeat <= 0:
    repeat = None
```

**`cron/jobs.py` — `mark_job_run()`**: add `times > 0` guard to the completion check

```python
if times is not None and times > 0 and completed >= times:
```

**`tools/cronjob_tools.py`** — same normalization on the update path

```python
normalized_repeat = None if repeat <= 0 else repeat
```

## Tests

Added two regression tests in `tests/cron/test_jobs.py`:
- `test_repeat_negative_one_is_infinite`: verifies `repeat=-1` is stored as `None` and the job survives 3 runs
- `test_repeat_zero_is_infinite`: verifies `repeat=0` is treated the same way

All 43 existing cron tests pass.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_jobs.py`