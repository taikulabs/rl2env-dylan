**feat(cli): add /update slash command to CLI and TUI**

## What does this PR do?

Makes the `/update` slash command available in the interactive CLI and TUI, not just the messaging gateway. Previously it was `gateway_only=True`, so users in the CLI/TUI had to exit and manually run `hermes update`. Now they can type `/update` directly.

- **Classic CLI**: prompts for confirmation, then `execvp`s `hermes update` (replaces the process so the user sees update output directly).
- **TUI**: exits with code 42 (a signal to the Python wrapper), which then `execvp`s `hermes update`.
- **Gateway**: unchanged — existing detached subprocess behavior continues to work.

## Related Issue

N/A — quality of life improvement.