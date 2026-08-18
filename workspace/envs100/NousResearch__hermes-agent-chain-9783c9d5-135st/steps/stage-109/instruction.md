**feat(browser): add Camofox local anti-detection browser backend**

## Summary

Adds Camofox as a local anti-detection browser backend. When `CAMOFOX_URL` is set, all 11 browser tools route through the Camofox REST API instead of the `agent-browser` CLI.

[Camofox-browser](https://github.com/jo-inc/camofox-browser) is a self-hosted Node.js server wrapping Camoufox (Firefox fork with C++ fingerprint spoofing). It bypasses bot detection at the engine level — not JS shims.

### Setup
```bash
# Option 1: npm
git clone https://github.com/jo-inc/camofox-browser && cd camofox-browser
npm install && npm start

# Option 2: Docker
docker run -p 9377:9377 jo-inc/camofox-browser
```

Then add to `~/.hermes/.env`:
```
CAMOFOX_URL=http://localhost:9377
```

### Tool mapping (1:1 coverage, 10 of 11)

| Tool | Camofox endpoint | Status |
|---|---|---|
| `browser_navigate` | `POST /tabs/:id/navigate` | ✓ |
| `browser_snapshot` | `GET /tabs/:id/snapshot` | ✓ |
| `browser_click` | `POST /tabs/:id/click` | ✓ |
| `browser_type` | `POST /tabs/:id/type` | ✓ |
| `browser_scroll` | `POST /tabs/:id/scroll` | ✓ |
| `browser_back` | `POST /tabs/:id/back` | ✓ |
| `browser_press` | `POST /tabs/:id/press` | ✓ |
| `browser_close` | `DELETE /sessions/:userId` | ✓ |
| `browser_get_images` | `GET /tabs/:id/images` | ✓ |
| `browser_vision` | `GET /tabs/:id/screenshot` + vision LLM | ✓ |
| `browser_console` | N/A (returns empty with note) | Limited |

### Architecture

- `tools/browser_camofox.py` — Full REST backend (~400 lines). Session management maps `task_id` → `(userId, tabId)`.
- `tools/browser_tool.py` — Each tool function checks `_is_camofox_mode()` at the top and delegates. SSRF/policy checks still apply for navigate.
- `hermes_cli/config.py` — `CAMOFOX_URL` env var entry.
- `check_browser_requirements()` returns `True` when camofox is configured (no agent-browser CLI needed).

### Advantages over Browserbase
- Free (no per-session API costs)
- Local (zero network latency)
- Anti-detection at C++ level (Cloudflare, Google)
- Works offline, Docker-ready
- ~40MB idle memory

### Tests
20 new tests covering all operations, routing integration, session lifecycle, and error handling. 74/74 total browser tests pass.