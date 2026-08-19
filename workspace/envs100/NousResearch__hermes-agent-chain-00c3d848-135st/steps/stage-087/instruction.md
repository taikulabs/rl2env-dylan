**fix(tui): route mutating slash commands through live gateway state**

## Summary
- add native TUI slash handlers for `/browser`, `/reload-mcp`, `/rollback`, `/stop`, `/fast`, and `/busy` so mutating operations hit live gateway RPCs instead of slash-worker fallback
- add TUI session lifecycle parity hooks in `tui_gateway/server.py` to commit memory and fire `on_session_finalize` / `on_session_reset` on close/new/resume boundaries
- add parity coverage: command-route matrix test over command registry entries plus focused slash and gateway tests for new native routes and config/session lifecycle behavior