**fix: backfill model on gateway sessions after agent runs**

## Summary
- salvage PR #997 onto current main by backfilling gateway session models after agent runs so sessions created before agent construction no longer remain `NULL` in SQLite
- preserve the contributor’s `COALESCE(model, ?)` behavior so existing session models are never overwritten
- add regression coverage for model backfill/preservation plus a small compatibility fix so `_run_agent()` tolerates fake agents and test doubles that do not define a `model` attribute

## Contributor credit
- substantive bugfix 
- follow-up tests and compatibility hardening added on top during salvage

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_session.py`
- `tests/test_hermes_state.py`