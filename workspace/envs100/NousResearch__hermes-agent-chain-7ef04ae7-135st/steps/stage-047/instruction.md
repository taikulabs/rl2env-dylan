**fix(security): prevent session-id path traversal in on-disk artifacts**

## Summary
A path-traversal–shaped session ID can no longer redirect Hermes' on-disk session artifacts outside `~/.hermes/sessions/`.

Root cause: the API server's `X-Hermes-Session-Id` continuation path only rejected `\r\n\x00` (header-injection chars) and never traversal sequences. That value flowed straight into `logs_dir / f"session_{sid}.json"` (and the request-dump path), so `../../../../outside/pwned` produced an arbitrary file write outside the sessions directory.

Salvage of #5958 by @Xowiek. The original diff predated a refactor (97 commits) that moved/removed two of its three patched sites, so it's rebuilt onto current `main` with their authorship preserved per-commit and the fix widened to the real sink sites plus the API entry boundary.

## Changes
**Sink — makes the bad write impossible regardless of entry point:**
- `run_agent.py`: `_safe_session_filename_component()` (Xowiek) collapses every non-`[A-Za-z0-9_-]` char to `_`, caps length, and appends a content hash when sanitized — always a single traversal-free segment. Wired into `_save_session_log`'s `session_{sid}.json` path.
- `agent/agent_runtime_helpers.py`: same sanitizer on the `request_dump_{sid}_{ts}.json` path.

**Boundary — clean 400 instead of a silently-hashed filename:**
- `gateway/platforms/api_server.py`: rejects traversal-shaped `X-Hermes-Session-Id` on the session-continuation path and the explicit `/api/sessions` create path, reusing `gateway.session._is_path_unsafe` (mirrors the native gateway's entry-boundary guard). Also enforces the session-header length cap on the continuation path.

## Validation
| Check | Result |
|---|---|
| E2E: traversal `session_id` → snapshot contained, nothing escapes to `../outside_dir` | pass |
| `tests/run_agent/test_run_agent.py` (+2: traversal-contained, sanitizer-invariant) | 13 pass |
| `tests/gateway/test_api_server.py` (+1: header rejects `../`, `/abs`, `..\win` → 400) | 10 pass |
| ruff | clean |

.

## Infographic
![session-id path traversal patched](https://v3b.fal.media/files/b/0aa03b79/vyuCnKNfu-DANeNFI25uY_zTHQjKmU.png)