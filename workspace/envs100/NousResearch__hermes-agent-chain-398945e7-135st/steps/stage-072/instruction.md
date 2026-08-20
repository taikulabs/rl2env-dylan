**fix: lazy session creation — defer DB row until first message**

## Problem

Empty sessions accumulate in `state.db` when the TUI/web dashboard is opened and closed without sending a message. Every TUI session eagerly creates a DB row within 50ms of opening, even if the user never interacts.

**Evidence**: 14 ghost sessions (zero messages, no title) found in state.db, all `source=tui`.

## Solution

Defer SQLite session row creation from `AIAgent.__init__` to `run_conversation()` entry — the moment the user actually sends a message.

### Key changes:

- **`run_agent.py`**: Add `_ensure_db_session()` gate method (boolean flag + error handling that disables `_session_db` on FK constraint risk). Called at top of `run_conversation()`. Remove eager `create_session()` from `__init__`.
- **`tui_gateway/server.py`**: Remove eager `db.create_session()` in `_start_agent_build()`. Add post-first-message `pending_title` re-apply hook.
- **`hermes_state.py`**: Extract `_insert_session_row()` shared helper (DRY — eliminates duplicate SQL between `create_session` and `ensure_session`). Add `prune_empty_ghost_sessions()` for one-time migration.
- **`cli.py`**: One-time ghost session prune on startup (scoped to `source=tui`, `NOT EXISTS(messages)`, 1hr age bound). Fix `_pending_title` to call `_ensure_db_session()` before `set_session_title()`.
- **`hermes_cli/main.py`**: Guard TUI exit summary — skip resume info when `message_count == 0`.

### What stays the same:
- CLI already lazy (no change needed)
- Gateway already message-triggered (no change needed)
- Session ID still generated at init (in-memory routing identifier)
- JSON session file still guarded by `if not messages: return`

## Other harness comparison

| Tool | Open → close without message | Session persisted? |
|------|-----|----|
| **Codex** | Zero artifacts | ❌ |
| **Claude Code (Ctrl+C×2)** | Nothing | ❌ |
| **Hermes CLI** | No DB row (already lazy) | ❌ |
| **Hermes TUI (before)** | DB row created eagerly | ✅ BUG |
| **Hermes TUI (after)** | No DB row | ❌ ✅ |

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_860_dedup.py`