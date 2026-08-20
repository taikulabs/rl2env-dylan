**fix: exclude Coding Plan-only models from Moonshot model selection**

## Summary
- salvage PR for #1045 preserving the contributor's fix on current main
- exclude Coding Plan-only models from the legacy Moonshot model selection path
- add regression coverage for Moonshot vs Coding Plan model list isolation

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_api_key_providers.py`