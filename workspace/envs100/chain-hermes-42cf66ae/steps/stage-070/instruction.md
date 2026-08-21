**feat: preload CLI skills on launch**

## Summary
- add a `--skills` / `-s` flag to `hermes` and `hermes chat`
- preload one or more skills into the session prompt before the first turn
- show a startup line before the CLI banner listing exactly which skills were activated
- reuse skill-loading helpers for both slash invocations and launch-time preloading, with tests and CLI docs updates

## Examples
- `hermes -s hermes-agent-dev,github-auth`
- `hermes -c -w -s hermes-agent-dev`
- `hermes chat -s github-pr-workflow -q "open a draft PR"`
- `hermes chat -s github-auth -s github-pr-workflow`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_skill_commands.py`
- `tests/hermes_cli/test_chat_skills_flag.py`
- `tests/test_cli_preloaded_skills.py`