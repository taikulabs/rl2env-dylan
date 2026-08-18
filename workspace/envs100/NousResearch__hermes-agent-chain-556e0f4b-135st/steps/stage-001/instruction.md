**feat: add Kilo Code (kilocode) as first-class inference provider**

## What this PR does

Reimplementation of PR #1473 by @amanning3390 onto current main.

Adds [Kilo Gateway](https://kilo.ai/gateway) as an API-key inference provider. Kilo provides a unified, OpenAI-compatible API to access 500+ models from Anthropic, OpenAI, Google, xAI, Mistral, MiniMax through a single endpoint and API key.

### Configuration
```yaml
model:
  provider: kilocode
  default: anthropic/claude-opus-4.6
```
```bash
# ~/.hermes/.env
KILOCODE_API_KEY=your-key
```

### Changes (11 files)
- **auth.py** — `kilocode` in PROVIDER_REGISTRY, aliases: `kilo`, `kilo-code`, `kilo-gateway`
- **models.py** — model catalog (Claude, GPT, Gemini families), labels, aliases, ordering
- **main.py** — CLI provider choices, model flow dispatch, static model list
- **setup.py** — setup wizard with API key prompt, model selection
- **doctor.py** — health check via `/models` endpoint
- **auxiliary_client.py** — default aux model: `google/gemini-3-flash-preview`
- **tests** — 12 new tests (registration, aliases, credentials, runtime)
- **docs** — env vars, config, fallback providers
- **test_setup_model_provider.py** — fix provider index shift from insertion

### Tests
4920 passed, 0 new failures (same 8 pre-existing).