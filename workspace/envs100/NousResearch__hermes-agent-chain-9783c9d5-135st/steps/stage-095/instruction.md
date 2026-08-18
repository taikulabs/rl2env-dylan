**fix: auxiliary client uses placeholder key for local servers without auth**

## Problem

Users running local inference servers (Ollama, llama.cpp, vLLM, LM Studio) without any cloud API keys get broken auxiliary operations — compression, summarization, and memory flush all fail because the auxiliary client skips their local server.

Root cause: `_resolve_custom_runtime()` in `auxiliary_client.py` requires both a `base_url` AND a non-empty `api_key`. Local servers don't need auth, so the key is empty → the function returns `(None, None)` → the auto-detection chain exhausts all options → `None` → timeouts and errors.

The main CLI already fixed this in PR #2556 with a `"no-key-required"` placeholder, but the auxiliary client's resolution path was never updated.

Symptoms in gateway logs:
```
WARNING resolve_provider_client: openrouter requested but OPENROUTER_API_KEY not set
WARNING Failed to generate context summary: Request timed out.
WARNING Session summarization failed after 3 attempts: Request timed out.
```

## Fix

- `_resolve_custom_runtime()`: use `"no-key-required"` placeholder when base_url is present but key is empty (matches cli.py pattern)
- `resolve_provider_client()` custom branch: same placeholder fallback for `explicit_base_url` without `explicit_api_key`
- Updated 2 tests that expected the old (broken) reject behavior