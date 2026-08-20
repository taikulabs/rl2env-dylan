**fix: surface gpt-5.4 in codex setup**

## Summary
- pass the live Codex OAuth access token into `get_codex_model_ids()` during `hermes setup`
- include `gpt-5.4` in Codex fallback catalogs so it still appears when live discovery is unavailable
- add a regression test covering the setup flow

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_setup.py`
- `tests/test_codex_models.py`