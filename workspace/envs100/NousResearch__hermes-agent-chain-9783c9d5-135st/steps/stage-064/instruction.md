**fix(gateway): inject PATH into launchd plist for macOS service**

## Summary

Salvage of PR #2173 (hanai, submitted first March 20) and PR #3432 (timknip, independent discovery March 27).

launchd services inherit a minimal PATH (`/usr/bin:/bin:/usr/sbin:/sbin`) which excludes Homebrew (`/opt/homebrew/bin` on Apple Silicon), nvm, cargo, etc. This causes the WhatsApp Node.js bridge to fail with `node not found`, even though node is installed and works in the user's shell.

### Code changes (`hermes_cli/gateway.py`)

**PATH injection** — snapshots the user's shell PATH at `hermes gateway install` time with three priority directories prepended:
1. `venv/bin` (or `.venv/bin`) — detected via `_detect_venv_dir()`, matching the systemd unit
2. `node_modules/.bin` — project-local node binaries, matching the systemd unit
3. Resolved `node` binary directory — explicit `shutil.which("node")` resolution so the node directory persists even if the user's shell PATH changes later

Duplicates are stripped via `dict.fromkeys()` to prevent PATH accumulation on gateway restart loops (where `refresh_launchd_plist_if_needed()` would detect spurious diffs).

**VIRTUAL_ENV** — added to the plist EnvironmentVariables for parity with the systemd unit. Tools that inspect VIRTUAL_ENV to resolve Python packages now work correctly under launchd.

**HERMES_HOME** — already present on main, preserved.

### Tests (7 new)

- Plist contains PATH, VIRTUAL_ENV, HERMES_HOME environment variables
- PATH includes venv/bin and it's first
- PATH includes node_modules/.bin
- PATH captures current shell PATH (`/custom/bin` via monkeypatch)
- PATH deduplicates venv/bin when already present
- All 644 hermes_cli tests pass

### Docs updates

- **messaging/index.md** — expanded macOS launchd section from 4 bare lines to full documentation with env var descriptions, PATH-changes-after-install tip, multiple-installations info
- **reference/faq.md** — new troubleshooting entry: "macOS: Node.js / ffmpeg / other tools not found by gateway" with PlistBuddy verification command
- **user-guide/messaging/whatsapp.md** — new troubleshooting row for "Node.js not installed but works in terminal" on macOS
- **guides/team-telegram-assistant.md** — updated macOS section to use `hermes gateway` commands instead of raw `launchctl`, added PATH tip

### Limitation (documented)

launchd plists are static files — PATH is captured at `hermes gateway install` time. If tools are installed after gateway setup, users need to re-run `hermes gateway install` to capture the updated PATH. This is documented in the messaging/index.md tip box and the FAQ entry.

## Credit

- **hanai** (PR #2173, submitted first) — original implementation with tests and deduplication
- **timknip** (PR #3432) — independent discovery, system dir fallback idea

,