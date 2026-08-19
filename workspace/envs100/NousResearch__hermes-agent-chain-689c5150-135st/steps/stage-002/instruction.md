**fix(cli): add ChatConsole.status compatibility for /skills search**

## Summary

Salvage of #7888 by @ktutumi. Cherry-picked onto current main.

Fixes a crash when using `/skills search <query>` in the interactive CLI:
```
Error: 'ChatConsole' object has no attribute 'status'
```

`hermes_cli/skills_hub.py` uses `console.status(...)` (introduced in #7301), but the interactive CLI passes `ChatConsole` which only implemented `print()`.

## Changes

- Add `ChatConsole.status()` as a no-op `@contextmanager` (silent because `_busy_command()` already shows progress)
- Add regression test exercising the `/skills search` path with `ChatConsole`