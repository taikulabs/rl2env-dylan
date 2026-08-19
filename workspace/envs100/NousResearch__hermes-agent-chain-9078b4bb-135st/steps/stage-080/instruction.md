**fix(security): deny root-level credential stores in media delivery**

## Summary
Credential stores that live at the `HERMES_HOME` root could be auto-attached to chat replies because the media-delivery denylist only enumerated four files. This adds the missing ones explicitly.

Root cause: `_media_delivery_denied_paths()` in `gateway/platforms/base.py` listed only `.env`, `auth.json`, `credentials`, `config.yaml` under the Hermes root. Everything else fell through. The reported leak: the Google Workspace skill rewrites `google_token.json` every turn, bumping its mtime to "now", which kept passing the strict-mode recency window (`trust_recent_files`) and re-sent the OAuth token on every reply.

## Changes
- `gateway/platforms/base.py`: extend the explicit per-file denylist under `_HERMES_HOME`/`_HERMES_ROOT` to mirror the canonical credential set already enforced by the read/write guards in `agent/file_safety.py`:
  - `google_token.json`, `google_oauth_pending.json`, `auth/google_oauth.json` (Google Workspace OAuth)
  - `.anthropic_oauth.json` (Anthropic PKCE refresh)
  - `webhook_subscriptions.json` (HMAC secrets)
  - `cache/bws_cache.json` (Bitwarden Secrets Manager plaintext cache)
  - `auth.lock`
  - `pairing/` directory (platform pairing tokens)
- `tests/gateway/test_platform_base.py`: 5 regression tests.

## Why targeted, not a whole-tree deny
The "deny the entire `~/.hermes` tree" approach was declined in #32090 and #34425 — it blocks legitimate workflows (skills, logs, ad-hoc agent-written files under `~/.hermes` that aren't in a cache subdir but are still expected to be deliverable). The maintainer's stated shape is a targeted addition to the explicit denylist for the specific leaking files. This PR follows that.

The allowlist (`MEDIA_DELIVERY_SAFE_ROOTS`, the cache subdirs) is matched **before** the denylist in `validate_media_delivery_path()`, so generated images/audio/video/documents still deliver.

Siblings in the same targeted shape (left out of this diff to avoid overlap): #37222 covers `mcp-tokens/`, #41071 covers `state.db`/`kanban.db`.

## Validation
| Path | Before | After |
|---|---|---|
| `~/.hermes/google_token.json` | delivered | **rejected** |
| `~/.hermes/google_token.json` (fresh mtime, strict mode) | delivered (recency bypass) | **rejected** |
| `~/.hermes/pairing/telegram-approved.json` | delivered | **rejected** |
| `~/.hermes/cache/documents/report.pdf` | delivered | delivered (allowlist wins) |
| `~/.hermes/adhoc_report.pdf` (recent) | delivered | delivered (tree NOT blanket-denied) |

- `scripts/run_tests.sh tests/gateway/test_platform_base.py` → 160 passed, 0 failed.
- E2E with real imports against a temp `HERMES_HOME`: `google_token.json` and `pairing/*` rejected; cache artifact and ad-hoc root file still delivered.

Reported-by: @xxxigm. .