**feat(doctor/status): surface xAI OAuth in display + suppress stale XAI_API_KEY (salvage #27196 + #27202 + #27210)**

## Summary
Combined salvage of #27196 + #27202 + #27210 (all stacked by the same author covering the same gap: xAI OAuth was the only OAuth provider missing from doctor/status display).

The official xAI OAuth merge added the provider plumbing but left three downstream surfaces silent about it.

## Changes
- `hermes_cli/doctor.py` — (1) extend `_has_healthy_oauth_fallback_for_apikey_provider()` to cover xAI so a stale `XAI_API_KEY` doesn't surface as a blocking error when xAI OAuth is healthy (sibling of the merged Gemini/MiniMax suppression); (2) add xAI OAuth row to the Auth Providers section (the existing block lists Gemini + MiniMax but skipped xAI); (3) isolate per-provider OAuth imports so one provider's import failure can't suppress the fallback check for the others.
- `hermes_cli/status.py` — list xAI OAuth alongside Nous / Qwen / MiniMax in the Auth Providers section.
- `tests/hermes_cli/test_doctor.py` + `test_status.py` — coverage for login/logout, error path, import-failure isolation, None-safety.

Four commits, all by @EloquentBrush0x — preserved via rebase-merge.

## Validation
- `scripts/run_tests.sh tests/hermes_cli/test_doctor.py tests/hermes_cli/test_status.py -q` → 73/73 pass.

Original PRs: #27196, #27202, #27210 — all three will be closed once this merges.