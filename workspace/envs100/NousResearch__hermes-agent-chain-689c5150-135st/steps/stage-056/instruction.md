**feat(providers): add Arcee AI as direct API provider**

## Summary

Adds Arcee AI as a standard direct API provider. `ARCEEAI_API_KEY` → `api.arcee.ai/api/v1`. Trinity models: `trinity-large-thinking`, `trinity-large-preview`, `trinity-mini`.

Arcee models are also already available via OpenRouter (`arcee-ai/trinity-large-thinking`) for users who prefer that route.

Salvaged from PR #9274 by @arthurbr11 — simplified from dual-endpoint OpenRouter routing to a standard direct provider.

### What changed from the original PR

The original PR had a dual-endpoint design where the `arcee` provider would auto-route to either Arcee's direct API or OpenRouter based on which key was present. This is unnecessary — users who want Arcee models via OpenRouter should just use `--provider openrouter` and pick `arcee-ai/trinity-large-thinking` from the model list (already present on main).

Stripped: `_resolve_arcee_base_url`, `_model_flow_arcee` (130 lines), `_arcee_route_is_openrouter()`, all OpenRouter routing logic. Arcee now uses the standard `_model_flow_api_key_provider` generic flow like xiaomi, minimax, etc.

### Files changed (19)

```
.env.example, agent/model_metadata.py, cli-config.yaml.example,
hermes_cli/auth.py, hermes_cli/config.py, hermes_cli/doctor.py,
hermes_cli/main.py, hermes_cli/model_normalize.py, hermes_cli/models.py,
hermes_cli/providers.py, hermes_cli/setup.py, trajectory_compressor.py,
tests/hermes_cli/test_arcee_provider.py,
website/docs/ (6 pages)
```