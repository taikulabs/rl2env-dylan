**fix(whatsapp): resolve LID↔phone aliases in allowlist matching**

## Summary

Salvage of the LID mapping fix from PR #1863. The rest of that PR (unauthorized_dm_behavior, WHATSAPP_REPLY_PREFIX, config version bumps, planning doc) was either already on main or unrelated.

## Problem

WhatsApp DMs can arrive with LID sender IDs (e.g. `900000000000001@lid`) even when `WHATSAPP_ALLOWED_USERS` is configured with phone numbers (e.g. `15550000001`). The existing allowlist check only stripped the `@` suffix but didn't resolve the phone↔LID mapping, so valid users were denied.

## Fix

Both the Python gateway and Node bridge now read the bridge session mapping files (`lid-mapping-*.json`) to resolve phone↔LID aliases:

- **gateway/run.py** — `_normalize_whatsapp_identifier()` strips JID/LID syntax, `_expand_whatsapp_auth_aliases()` walks mapping files to build a full alias set. `_is_user_authorized()` expands both the allowlist entries and the sender ID before matching.
- **scripts/whatsapp-bridge/allowlist.js** — Extracted allowlist logic into a shared module with the same mapping-file resolution. `bridge.js` now uses `matchesAllowedUser()` instead of a simple array `.includes()`.

## Tests

- 1 new Python test: LID sender matches phone allowlist via session mapping files
- 3 Node tests: normalize, expand, matchesAllowedUser
- 1641 gateway tests pass (7 pre-existing boot-md hook failures, unrelated)

EOF; __hermes_rc=$?; printf '__HERMES_FENCE_a9f7b3__'; exit $__hermes_rc