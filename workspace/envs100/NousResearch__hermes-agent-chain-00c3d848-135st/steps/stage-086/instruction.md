**feat(providers): add GMI Cloud as first-class API-key provider**

## Summary

Salvage of #11955 (GMI Cloud first-class provider) by @isaachuangGMICLOUD, cherry-picked onto current `main` with conflict resolution and review fixes applied in a follow-up commit.

---

### What this adds

GMI Cloud (`api.gmi-serving.com`) as a full first-class API-key provider — on par with `arcee`, `kilocode`, `xiaomi`, etc.:

- **`hermes_cli/auth.py`** — `ProviderConfig` (`id="gmi"`, `auth_type="api_key"`, `GMI_API_KEY` / `GMI_BASE_URL`)
- **`hermes_cli/providers.py`** — `HermesOverlay` with `extra_env_vars=("GMI_API_KEY",)` (needed for models.dev detection since GMI isn't in models.dev yet)
- **`hermes_cli/models.py`** — curated vendor/model catalog (slash-form, GMI is a multi-vendor aggregator); live `/v1/models` fetch with static fallback; `CANONICAL_PROVIDERS` entry
- **`hermes_cli/main.py`** — `"gmi"` in both `_named_custom_provider_map` tuple and `--provider` argparse choices; dispatches to `_model_flow_api_key_provider` generically
- **`agent/model_metadata.py`** — `_URL_TO_PROVIDER["api.gmi-serving.com"] = "gmi"`; `_PROVIDER_PREFIXES` entries; dedicated context-length probe block (GMI's `/models` endpoint has authoritative `context_length` data, and it's a known URL so the generic custom-endpoint probe skips it)
- **`agent/auxiliary_client.py`** — provider aliases; `_compat_model` fix to preserve slash-form model IDs on cached aggregator-style clients; `gmi` aux model entry
- **`hermes_cli/doctor.py`** — GMI in provider connectivity checks
- **`hermes_cli/config.py`** — `GMI_API_KEY` / `GMI_BASE_URL` in `OPTIONAL_ENV_VARS`
- **`tests/conftest.py`** — explicit `GMI_BASE_URL` clearing (not caught by `_API_KEY` suffix pattern)
- **Docs** — `providers.md`, `environment-variables.md`, `cli-commands.md`, `fallback-providers.md`, `configuration.md`, `quickstart.md` (expands provider table)

### Aliases

`gmi`, `gmi-cloud`, `gmicloud` all resolve to canonical `gmi`.

### Provider flow coverage (verified against `arcee` pattern)

| Touchpoint | Status |
|---|---|
| `auth.py` ProviderConfig | ✓ |
| `providers.py` HermesOverlay | ✓ |
| `models.py` `_PROVIDER_MODELS` + `CANONICAL_PROVIDERS` + `_PROVIDER_LABELS` + `_PROVIDER_ALIASES` | ✓ |
| `models.py` `provider_model_ids()` live fetch | ✓ |
| `main.py` `_named_custom_provider_map` + `--provider` choices + `_model_flow_api_key_provider` dispatch | ✓ |
| `model_metadata.py` `_URL_TO_PROVIDER` + `_PROVIDER_PREFIXES` + context-length probe | ✓ |
| `auxiliary_client.py` aliases + `_API_KEY_PROVIDER_AUX_MODELS` | ✓ |
| `doctor.py` connectivity check | ✓ |
| `config.py` `OPTIONAL_ENV_VARS` | ✓ |
| `runtime_provider.py` | ✓ (generic `resolve_api_key_provider_credentials` path, no changes needed) |
| `setup.py` | ✓ (unified since March 2026 — auto-inherits from `main.py` dispatch) |
| `status.py` | ✓ (uses generic `resolve_provider()` + `provider_label()`) |
| `fallback_providers.md` table | ✓ |
| `providers.md` inline fallback list | ✓ |
| `environment-variables.md` | ✓ |
| `cli-commands.md` `--provider` list | ✓ |
| `conftest.py` hermetic env | ✓ |

---

### Changes from original PR (follow-up commit)

| Issue | Fix |
|---|---|
| `ENV_VARS_BY_VERSION[17]` is dead code — current `_config_version` is 22, so no existing user would ever be prompted | Removed; matches how `arcee` was added (no version entry) |
| `_API_KEY_PROVIDER_AUX_MODELS["gmi"] = "anthropic/claude-opus-4.6"` — most expensive model, inconsistent with other providers (all use cheap flash/turbo variants) | Changed to `google/gemini-3.1-flash-lite-preview` (already in GMI's curated catalog) |
| Test `write_text("GMI_API_KEY=*** encoding="utf-8")` — mismatched quote, writes literal `"GMI_API_KEY=*** encoding="` to `.env` file | Fixed to `write_text("GMI_API_KEY=***\n", encoding="utf-8")` |
| `providers.md` inline "Supported providers" fallback list (line ~1181) missing `gmi` | Added |
| `cli-commands.md` `--provider` choices list missing `gmi` | Added |
| Conflict resolution in `test_auxiliary_client.py` left

…(truncated)