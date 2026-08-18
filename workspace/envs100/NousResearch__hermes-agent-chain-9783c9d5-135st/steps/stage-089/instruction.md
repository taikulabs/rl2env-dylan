**fix(auth): stop silently falling back to OpenRouter when no provider is configured**

## Summary

Stops Hermes from silently falling back to OpenRouter + Claude Opus when no provider is configured. Users now get a clear error with setup instructions instead of being routed to a provider they never intended.

Motivated by [a user in Discord](https://discord.com) who set `provider: lmstudio`, got "Unknown provider 'lmstudio'", reinstalled, and then had their local Qwen 3.5 9B model confidently claiming to be Claude Opus via OpenRouter — because every fallback path defaulted there.

## Changes

**auth.py:**
- `resolve_provider()` final fallback now raises `AuthError("No inference provider configured. Run 'hermes model'...")` instead of silently returning `"openrouter"`
- Added local server aliases: `lmstudio`, `lm-studio`, `lm_studio`, `ollama`, `vllm`, `llamacpp`, `llama.cpp`, `llama-cpp` → all map to `"custom"`

**gateway/run.py + cron/scheduler.py:**
- Removed hardcoded `"anthropic/claude-opus-4.6"` model fallback — these now use `""` and read from config.yaml like everything else

**cli-config.yaml.example:**
- Complete provider documentation listing all supported providers, required keys, and local server setup instructions with examples

## What this prevents

- User configures a local server but misspells the provider → clear error instead of silent OpenRouter routing
- Fresh install with no API keys → clear "run hermes model" guidance instead of trying OpenRouter with no key
- Local Qwen/Llama model claiming to be Claude because the default model name was `anthropic/claude-opus-4.6`

## Tests
- 258 auth/provider/fallback tests pass
- Updated `test_auto_does_not_select_copilot_from_github_token` to expect AuthError instead of "openrouter" fallback