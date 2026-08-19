**fix(update): stream npm install output so postinstall progress is visible**

Salvages @briandevans's #18869 onto current main. PR #27055 already removed the worst offender (`@askjo/camofox-browser`) from eager root deps, but the remaining root + ui-tui npm installs still ran with `--silent` + `capture_output=True`, so any future binary-postinstall package (or `agent-browser`'s Chromium fetch on a fresh install) would still look like `hermes update` is frozen.

## Summary

Drop `--silent` and pass `capture_output=False` for the repo-root and ui-tui npm installs in `_update_node_dependencies()` so npm streams its `info run …` postinstall lines straight to the terminal. The existing `_UpdateOutputStream` wrapper mirrors output to `~/.hermes/logs/update.log`, so SSH-disconnect safety is preserved.

The `web/` install path is intentionally untouched — its build step is short and does not run binary-fetching postinstalls.

## Changes

- `hermes_cli/main.py` `_update_node_dependencies()`: drop `--silent` from repo-root + ui-tui flags, pass `capture_output=False`. Defensive stderr guard for the streamed path.
- `tests/hermes_cli/test_cmd_update.py`: assert the new flag set + assert `capture_output is False` for repo-root and ui-tui calls. Web install assertion preserved.

Refreshed Brian's comment in main.py to reference `agent-browser`'s Chromium fetch as the remaining example (Camofox is no longer eager after #27055).

## Validation

- `tests/hermes_cli/test_cmd_update.py` — 10/10 pass
- `tests/hermes_cli/test_web_ui_build.py`, `test_tui_npm_install.py` — green
- 

## Credit

Authored by @briandevans. Cherry-picked onto current main with conflict resolution against the recently-evolved `test_update_refreshes_repo_and_tui_node_dependencies` test. Original PR will be closed with a credit comment after merge.

.
Supersedes #18869.