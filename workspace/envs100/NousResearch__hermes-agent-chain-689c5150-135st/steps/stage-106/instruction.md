**fix(memory): discover user-installed memory providers from $HERMES_HOME/plugins/**

## Summary

Memory provider discovery (`discover_memory_providers()`, `load_memory_provider()`) only scanned the bundled `plugins/memory/` directory inside the hermes-agent source tree. User-installed providers at `$HERMES_HOME/plugins/<name>/` were invisible to `hermes memory setup` and `hermes memory status`.

This forced users to symlink into the repo source tree:
```bash
ln -s ~/.hermes/plugins/<name> plugins/memory/<name>
```

This workaround broke on `hermes update` (resets the source tree) and created a **dual-registration path** — the general plugin system loaded the plugin from `~/.hermes/plugins/` AND the memory provider system loaded it from the symlink in `plugins/memory/`. This produced duplicate tool names in the API request, causing 400 errors on strict providers like Xiaomi MiMo via Nous Portal.

### What changed

**`plugins/memory/__init__.py`:**
- `_get_user_plugins_dir()` — resolves `$HERMES_HOME/plugins/`
- `_is_memory_provider_dir()` — heuristic text scan for `MemoryProvider` or `register_memory_provider` in source (filters out non-memory user plugins)
- `_iter_provider_dirs()` — scans bundled first, then user-installed; deduplicates by name (bundled wins)
- `find_provider_dir()` — public resolver, bundled-first lookup
- `discover_memory_providers()` → now uses `_iter_provider_dirs()`
- `load_memory_provider()` → now uses `find_provider_dir()`
- `discover_plugin_cli_commands()` → now uses `find_provider_dir()`
- User plugins use `_hermes_user_memory.<name>` namespace to avoid `sys.modules` collisions with bundled `plugins.memory.<name>`

**`hermes_cli/memory_setup.py`:**
- `_install_dependencies()` → uses `find_provider_dir()` instead of hardcoded bundled path

### Design decisions

- **Bundled always wins** on name collisions (via `seen` set / bundled-first check)
- **Non-memory plugins excluded** via cheap source-text heuristic (no import needed)
- **Separate sys.modules namespace** for user plugins prevents import conflicts

### Test results

- 57 unit tests pass (4 new: discovery, loading, precedence, filtering)
- 261 run_agent + plugin CLI tests pass
- E2E verified with real file I/O: user plugin discovered, loaded, tools returned, non-memory plugins excluded

, #9099. Supersedes #4987, #9123, #9130, #9132, #9982.