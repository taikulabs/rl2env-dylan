**fix: add macOS Homebrew paths to browser and terminal PATH resolution**

## Problem

On macOS with Homebrew (Apple Silicon), Hermes runs with a filtered PATH that doesn't include Homebrew directories like `/opt/homebrew/bin/` or versioned node paths like `/opt/homebrew/opt/node@24/bin/`. This causes browser tools to fail with:

```
env: node: No such file or directory
```

The `agent-browser` package needs `node` to launch headless Chromium, but the `_SANE_PATH` fallback in `browser_tool.py` and `environments/local.py` only included standard Linux paths.

## Changes

- **`_SANE_PATH` updated** in both `browser_tool.py` and `environments/local.py` to include `/opt/homebrew/bin` and `/opt/homebrew/sbin` (Apple Silicon Homebrew defaults)
- **New `_discover_homebrew_node_dirs()`** function finds versioned Node.js installs (e.g. `brew install node@24`) that aren't linked into `/opt/homebrew/bin` — globs `/opt/homebrew/opt/node*/bin/`
- **`_find_agent_browser()` extended** to search Homebrew dirs, Hermes-managed node, and versioned Homebrew node dirs when `agent-browser` isn't on the current PATH
- **Subprocess PATH enriched** in `_run_browser_command()` to include discovered Homebrew node directories

On non-macOS systems, these paths don't exist so the `os.path.isdir()` checks prevent them from being added — zero impact on Linux.

## Tests

11 new tests in `tests/tools/test_browser_homebrew_paths.py`:
- `_SANE_PATH` includes Homebrew directories
- `_discover_homebrew_node_dirs()` finds versioned dirs, excludes unversioned, handles errors
- `_find_agent_browser()` searches extended paths, finds npx in Homebrew, raises when not found

All 84 browser + local environment tests pass.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_browser_homebrew_paths.py`
- `tests/tools/test_local_env_blocklist.py`