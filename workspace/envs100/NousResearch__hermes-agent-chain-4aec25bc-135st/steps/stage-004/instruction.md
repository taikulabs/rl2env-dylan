**fix(windows): silence tirith-unavailable CLI banner on platforms with no tirith build**

## Summary
Stops Hermes from showing a scary `tirith security scanner enabled but not available` banner on every Windows CLI startup. Tirith ships no Windows binary, so the warning was pure noise — pattern-matching guards still run, and the user couldn't act on it.

Also stops the background install thread, PATH probes, disk failure-marker writes, and per-command spawn attempts on unsupported platforms — they were dead work that bought nothing.

## Changes
- `tools/tirith_security.py`: new public `is_platform_supported()` (returns False on Windows / unknown arch). `ensure_installed()`, `_resolve_tirith_path()`, and `check_command_security()` short-circuit silently on unsupported platforms. Explicit user-configured `tirith_path` still honored (WSL build-it-yourself case).
- `cli.py`: banner gated on `is_platform_supported()` — fires only when tirith *could* work but isn't installed.
- `website/docs/user-guide/security.md`: notes supported-platform list (Linux x86_64/aarch64, macOS x86_64/arm64), points Windows users at WSL.
- `tests/tools/test_tirith_security.py`: +8 tests (`TestUnsupportedPlatform`) covering the platform-detection matrix and the silent fast-paths at all three entry points.

## Validation
|                              | Before                                                     | After                                |
|------------------------------|------------------------------------------------------------|--------------------------------------|
| Windows CLI startup          | `⚠ tirith security scanner enabled but not available`     | Silent                               |
| Windows `ensure_installed` | Probes PATH + spawns daemon download thread that fails     | Returns None immediately, no thread  |
| Windows per-command scan     | `subprocess.run(["tirith", …])` → OSError every call     | `allow` short-circuit, no spawn     |
| Linux / macOS                | Unchanged                                                  | Unchanged                            |
| `test_tirith_security.py`  | 67 passed                                                  | 75 passed (8 new)                    |
| `test_command_guards.py`   | 19 passed                                                  | 19 passed                            |

E2E verified locally with `platform.system()` mocked to `Windows` / `AMD64`: `is_platform_supported() == False`, `ensure_installed()` returns `None` without spawning a thread or calling `shutil.which`, `check_command_security()` returns `{"action": "allow", …}` without calling `subprocess.run`.