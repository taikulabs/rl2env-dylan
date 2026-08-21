**fix: use skill activity in curator status**

## Summary

- Derive `last_activity_at` and `activity_count` from skill use/view/patch telemetry.
- Use `last_activity_at` for curator automatic lifecycle transitions, so recently viewed or patched skills are not falsely marked stale.
- Update `hermes curator status` and curator candidate rendering to show activity instead of only `last_used_at`.
- Add regression coverage for activity derivation, false stale prevention, and CLI status output.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_curator_activity.py`
- `tests/hermes_cli/test_curator_status.py`
- `tests/tools/test_skill_usage.py`