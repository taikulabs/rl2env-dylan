**fix(security): harden dashboard API against unauthenticated access**

## Summary

Addresses responsible disclosure from FuzzMind Security Lab (Callum @0xca1x, @migraine-sudo).

The web dashboard API server had 36 endpoints, of which only 5 checked the session token. The token itself was served from an unauthenticated `GET /api/auth/session-token` endpoint, rendering the protection circular. When bound to `0.0.0.0` (`--host` flag), all API keys, config, and cron management were accessible to any machine on the network.

## Changes

- **Auth middleware** — requires session token on ALL `/api/` routes except a small public whitelist (`/api/status`, `/api/config/defaults`, `/api/config/schema`, `/api/model/info`)
- **Remove token endpoint** — `GET /api/auth/session-token` deleted; token is now injected into `index.html` via a `<script>` tag at serve time so only the actual SPA has it
- **Timing-safe comparison** — all token checks now use `hmac.compare_digest()` instead of `!=`
- **Block public binding** — non-localhost `--host` now requires `--insecure` flag (hard error without it)
- **Frontend** — `fetchJSON()` sends Authorization header on all requests using `window.__HERMES_SESSION_TOKEN__`