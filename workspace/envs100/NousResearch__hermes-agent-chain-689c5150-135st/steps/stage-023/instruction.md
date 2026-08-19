**feat: add WSL environment hint to system prompt**

## Summary

When running inside WSL (Windows Subsystem for Linux), inject a hint into the system prompt so the agent knows the Windows host filesystem is mounted at `/mnt/c/`, `/mnt/d/`, etc.

**User problem:** WSL users had to manually explain path translation every session (e.g., "my files are at /mnt/c/Users/Administrator/Desktop/"). Multiple AI chat models gave different solutions — this makes it automatic.

**Approach:** Detect WSL via the existing `is_wsl()` from `hermes_constants` (cached, checks `/proc/version` for 'microsoft'). Add a `build_environment_hints()` function in `prompt_builder.py` that returns environment-specific guidance. Called from `_build_system_prompt()` right before platform hints.

The hint tells the agent:
- It's running inside WSL
- Windows filesystem is at `/mnt/c/`, `/mnt/d/`, etc.
- User files typically at `/mnt/c/Users/<username>/Desktop/`, etc.
- Can list `/mnt/c/Users/` to discover the Windows username

**Extensible:** `build_environment_hints()` is designed to be extended for Termux, Docker, and other environments later.

## Changes
- `agent/prompt_builder.py` — `WSL_ENVIRONMENT_HINT` constant + `build_environment_hints()` function
- `run_agent.py` — Call `build_environment_hints()` in `_build_system_prompt()`
- `tests/agent/test_prompt_builder.py` — 3 tests for the constant and function