**feat(dep_ensure): complete Windows bootstrap — dep_ensure + install.ps1 + detection**

## Summary
- `dep_ensure.py`: Windows awareness (`_IS_WINDOWS`, PowerShell invocation, `(path, shell)` tuple returns)
- `install.ps1`: `-Ensure`/`-PostInstall` modes with `npm -g --prefix` (matches install.sh) and `agent-browser install` for Chromium
- `browser_tool.py`: adds `~/.hermes/node/` to candidate dirs for Windows `.cmd` shim detection
- Both install scripts bundled in pip wheel (pyproject.toml + CI)

## Design decisions
- **`npm -g --prefix`** on both platforms (not local install) — one install path, one detection path
- **`agent-browser install`** instead of `npx playwright install` — works with global prefix, avoids invalid `--yes` flag
- **browser_tool.py updated in same PR** — no knowingly-broken paths land

Tracking: #27826