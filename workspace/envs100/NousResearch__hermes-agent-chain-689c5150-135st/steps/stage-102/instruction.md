**fix: /debug privacy — auto-delete pastes after 1 hour, add privacy notices**

## Summary

Addresses user privacy concern from Discord where `/debug` uploaded full conversation logs to a public paste service with no warning, no expiry, and no way to delete.

### Changes

**Auto-delete (1 hour TTL):**
- After uploading to paste.rs, a detached background process is spawned that sleeps for 1 hour then sends HTTP DELETE requests to clean up the pastes
- Uses `start_new_session=True` so the cleanup survives the parent process exiting (important for CLI mode)
- Best-effort — if the cleanup process dies, `hermes debug delete <url>` is available as a manual fallback

**Privacy notices:**
- CLI `hermes debug share`: Shows a clear warning listing exactly what data will be uploaded before proceeding
- Gateway `/debug`: Shows privacy notice in the response message

**Gateway: reduced data exposure:**
- Gateway `/debug` now only uploads the summary report (system info + recent log tails), NOT full log files containing conversation content
- Users who need full logs can use `hermes debug share` from the CLI

**Manual delete command:**
- `hermes debug delete <url> [<url>...]` — sends DELETE to paste.rs for immediate cleanup
- Works as a fallback if the auto-delete process doesn't fire

### Files changed
- `hermes_cli/debug.py` — auto-delete scheduling, privacy notices, delete helpers, delete CLI handler
- `gateway/run.py` — gateway /debug: summary-only upload, privacy notice, auto-delete
- `hermes_cli/main.py` — `hermes debug delete` argparse subcommand
- `tests/hermes_cli/test_debug.py` — 16 new tests (45 total, all passing)