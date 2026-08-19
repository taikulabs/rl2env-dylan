**fix(discord): authorize pairing-approved users for component button clicks**

Salvage of #50633 (@liuhao1024) onto current `main`. .

## Summary
Discord approval/component buttons now authorize pairing-approved users again, restoring the v0.16 behavior that the v0.17 bundled-plugin migration regressed.

## Root cause
The v0.17 bundled-plugin migration (`cc8e5ec2a`) routed Discord component (button) interactions through `_component_check_auth`, which authorizes only against `DISCORD_ALLOWED_USERS` / `GATEWAY_ALLOWED_USERS` / role allowlists. The gateway **message** path (`gateway/authz_mixin`) is broader — it *always* consults the pairing store (`is_approved`) regardless of allowlists. So a user paired via `hermes pairing approve` but not in `DISCORD_ALLOWED_USERS` could send messages (accepted at the message gate) yet was rejected at approval buttons with "You're not authorized to approve commands."

## Fix
`_component_check_auth` now consults the pairing store as a fallback after the existing allowlist/role checks — mirroring the message path. `PairingStore` is stateless and file-backed (`PAIRING_DIR`), so a fresh instance reads the same approved set the gateway runner uses. All five component views (Exec approval, slash confirm, update prompt, model picker, clarify) are fixed at the single shared chokepoint. Fails closed: an import/lookup error falls through to allowlist-only behavior. Allow-all and allowlist paths are untouched, and admin/slash-access scope (`slash_access.py`) is deliberately not involved — button clicks are a user-scope admission action, exactly as the message path treats them.

## Changes
- `plugins/platforms/discord/adapter.py`: pairing-store fallback in `_component_check_auth`; resolve user id once for both allowlist and pairing checks.
- `tests/gateway/test_discord_component_auth.py`: +3 tests (pairing-approved authorized without allowlist, non-approved rejected, import-error fails closed).

## Validation
| Case | Before | After |
|---|---|---|
| Paired user, no allowlist | rejected at buttons | authorized |
| Unpaired user, no allowlist | rejected | rejected (fail closed) |
| Allowlisted user | authorized | authorized |

Targeted suite green (31/31). E2E verified against a real file-backed `PairingStore` with real imports and a temp `HERMES_HOME`.

Co-authored credit: @liuhao1024 (implementation). Also reported-to-PR by @LeonSGP43 and @ahmadalzaro1.

## Infographic

![discord-button-auth-restored](https://v3b.fal.media/files/b/0a9f8c81/-SLWjeTHuqN8bQA1CK4tn_V6UbCsBS.png)