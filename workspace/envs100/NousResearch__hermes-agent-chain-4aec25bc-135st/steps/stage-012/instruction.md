**fix(copilot-acp): salvage #10685 — tighter deprecation detection + sharper 8K-cap hint ()**

Salvage of @konsisumer's #10685 onto current main with follow-up improvements.

## What this PR makes true
Spawning the deprecated `gh copilot` extension via ACP mode now surfaces an actionable error pointing the user at `npm install -g @github/copilot` (the actual CLI Hermes wants), and hitting `models.inference.ai.azure.com`'s 8K cap stops three rounds of futile compression — we tell the user the endpoint is incompatible and what to use instead.

## 
- f01bf2a — detect gh-copilot deprecation, recognize Azure GitHub Models URL, emit 413 hint
- 66b4ff7 — tests for deprecation detection + URL mapping

## Follow-up )
1. **Tightened deprecation detection.** The previous list (`'has been deprecated'`, `'no commands will be executed'`, `'deprecation'`, `'copilot-cli'`) would false-positive on stderr from the NEW `@github/copilot` CLI — whose repo is literally `github.com/github/copilot-cli` and which surfaces "copilot-cli" / "deprecation" in legitimate messages. Now requires BOTH a product fingerprint (`gh-copilot`) AND a deprecation marker.
2. **Corrected the install hint.** The user in #10648 installed `gh extension install github/gh-copilot` thinking that was what ACP needs. ACP actually spawns the new `copilot` binary from `@github/copilot`. New error message leads with `npm install -g @github/copilot` and the new CLI's repo URL; provider-switching demoted to fallback.
3. **`_URL_TO_PROVIDER` consistency.** Azure URL value changed from `'github-models'` (alias) to `'copilot'` (canonical), matching the convention used by `api.githubcopilot.com` and `models.github.ai`.
4. **Sharpened the 8K hint.** The free tier's ~8K cap is below Hermes' system-prompt + tool-schemas floor, so the endpoint is fundamentally incompatible with an agentic loop — not a 'use a different URL' problem. Says so directly.

## Validation
- `scripts/run_tests.sh tests/agent/test_copilot_acp_deprecation.py`: 14/14
- `scripts/run_tests.sh tests/agent/test_model_metadata.py tests/hermes_cli/test_model_validation.py tests/hermes_cli/test_api_key_providers.py`: 353/354 (1 pre-existing failure on main: `test_auto_does_not_select_copilot_from_github_token` — unrelated)
- E2E import sanity-check: real banner detected, new-CLI stderr NOT misclassified, Azure URL → `'copilot'` via `_infer_provider_from_url`, base-URL recognition covers both Azure and github.ai endpoints.

.