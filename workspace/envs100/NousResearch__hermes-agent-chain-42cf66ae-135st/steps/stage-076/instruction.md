**fix: restore config-saved custom endpoint resolution**

## Summary
- honor config-saved custom endpoint base URLs during main runtime resolution when provider=custom
- route auxiliary text/vision/main-provider resolution through the same custom endpoint logic
- add regression tests for config-only custom endpoint setups

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_auxiliary_client.py`
- `tests/test_runtime_provider_resolution.py`