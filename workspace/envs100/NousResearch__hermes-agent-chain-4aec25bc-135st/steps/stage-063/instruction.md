**fix(auth): copy-pasteable SSH tunnel hint with auto-detected user@host**

Salvage of #27126 by @konsisumer cherry-picked onto current main.

## Summary
The SSH-tunnel hint shown during xAI/Spotify OAuth on remote sessions printed `<user>@<this-host>` placeholders that the user had to hand-edit before pasting. Now auto-detects via `$USER` / socket.gethostname() so the command is paste-ready.

## Changes
- `hermes_cli/auth.py`: `_ssh_user_at_host()` helper with fallbacks (USER → LOGNAME → `<user>`, gethostname with OSError + empty-string guards), visual header divider, 'SSH tunnel required' wording. Pure ASCII — safe on no-color/dumb terminals.
- `tests/hermes_cli/test_auth_loopback_ssh_hint.py`: 14 tests covering all fallback paths.

## Validation
`scripts/run_tests.sh tests/hermes_cli/test_auth_loopback_ssh_hint.py` → 14/14 passing.

 (salvage merge — author preserved).