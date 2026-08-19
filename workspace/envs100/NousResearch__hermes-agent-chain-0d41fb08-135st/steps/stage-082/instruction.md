**fix(browser): hardening — dead code, caching, scroll perf, security, thread safety**

## Summary

Salvaged from PR #7276 by @kshitijk4poor. The original commit included 6 new browser tools and unrelated scope additions beyond what the PR description stated — this salvage extracts only the hardening changes described in the PR.

## What changed (tools/browser_tool.py, +135/-64 lines)

### Bug fix
- **`_camofox_eval` wrong call signatures** — `_ensure_tab(session)` passed a dict where `task_id: str` was expected; `_post(..., json_data=...)` used wrong kwarg name (`body=` is correct). Function always raised TypeError — effectively dead code.

### Dead code removal
- **`DEFAULT_SESSION_TIMEOUT = 300`** — defined, never referenced anywhere
- **`browser_close` schema** — defined in `BROWSER_TOOL_SCHEMAS` but never registered via `registry.register()`. No handler exists. Saves ~150 tokens per API call.

### Performance: caching
- **`_find_agent_browser()`** — was doing `shutil.which()` + filesystem scans on every browser command. Now cached after first resolution, cleared on `cleanup_all_browsers()`.
- **`_get_command_timeout()`** — was parsing `config.yaml` from disk on every call. Now resolve-once cached.
- **`_discover_homebrew_node_dirs()`** — was scanning `/opt/homebrew/opt` on every call. Now `@functools.lru_cache(maxsize=1)`.

### Performance: scroll optimization
- **Single pixel-arg scroll** — replaced the 5× subprocess loop with a single call using agent-browser's pixel argument: `scroll down 500`. Eliminates 4 unnecessary subprocess spawns per scroll (~80-200ms saved on macOS). Camofox path retains the loop since its REST API doesn't support pixel args.

### Security
- **URL-decoded secret exfiltration check** — now checks both the raw URL and `urllib.parse.unquote(url)`, preventing bypass via URL-encoded API keys (e.g., `sk%2Dant%2D...`).

### Thread safety
- **`_recording_sessions` protected by `_cleanup_lock`** — the set was previously accessed without locks from concurrent subagent threads. All access points (check membership, add, discard, clear) now wrapped in `with _cleanup_lock:`.

### Error handling
- **Empty stdout = failure** — when `_run_browser_command` gets empty stdout with rc=0, it now returns failure instead of silently returning success. Whitelisted commands (`close`, `record`) via module-level `_EMPTY_OK_COMMANDS` frozenset.

### Token optimization
- **Structure-aware `_truncate_snapshot`** — cuts at line boundaries instead of mid-element, preserving complete accessibility tree entries.

## Follow-up fixes (not in original PR)
- Moved `_EMPTY_OK_COMMANDS` to module-level frozenset (was per-call set allocation in contributor's code)
- Fixed list+tuple concatenation bug in `_run_browser_command` PATH construction (return type change to tuple needed `list()` wrapper at one call site)
- Added cache-clearing autouse fixture to `test_browser_homebrew_paths.py`

## Test results
17 new tests + 148 existing browser tests = **165 passed, 0 failed** (1 pre-existing config version mismatch failure in `test_browser_camofox_state.py`, unrelated).

, , , 
Salvages #7276