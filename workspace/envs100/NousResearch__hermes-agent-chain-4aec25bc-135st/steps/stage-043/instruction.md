**fix(doctor): flag missing credentials for active openrouter provider (salvage #26453)**

## Summary
Salvage of #26453 — `hermes doctor` excluded `openrouter` from its API-key credential check (along with `custom`/`auto`), so a user whose `model.provider` is set to `openrouter` but has neither `OPENROUTER_API_KEY` nor `OPENAI_API_KEY` configured would see no blocking error from doctor — yet hermes runtime then fails with `No LLM provider configured`. The doctor's whole job is to flag exactly this.

## Changes
- `hermes_cli/doctor.py` — remove `openrouter` from the exclusion list and add a dedicated branch that checks `OPENROUTER_API_KEY` or `OPENAI_API_KEY` (the legacy fallback). All other API-key providers continue through the `PROVIDER_REGISTRY` path.
- `tests/hermes_cli/test_doctor.py` — regression test asserting the failure surfaces when both env vars are missing on an openrouter-active config.

## Validation
- `scripts/run_tests.sh tests/hermes_cli/test_doctor.py -q` → 57/57 pass.

Resolves the user-facing case in issue #26436.

Original PR: #26453 — credit preserved via rebase-merge (commit had `YOUR_GITHUB_EMAIL` placeholder; re-authored to your GitHub noreply).