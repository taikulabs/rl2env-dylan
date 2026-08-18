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