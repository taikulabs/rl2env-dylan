**refactor(bootstrap): consolidate ACP browser bootstrap into install.{sh,ps1}**

## Summary
- Delete `acp_adapter/bootstrap/` (687 lines of duplicated browser bootstrap)
- `_run_setup_browser()` now routes through `dep_ensure.ensure_dependency()` instead of shelling to custom scripts
- `install.sh` gains `ensure_browser()` with `npm -g --prefix`, macOS app-bundle detection, and per-distro hints
- `ensure_mode()` and `postinstall_mode()` browser cases simplified to call `ensure_browser()`
- `configure_browser_env_from_system_browser()` fixed for pip users (creates `.env` if missing)

Stacked on #27845 (sid/windows-bootstrap)

Tracking: #27826