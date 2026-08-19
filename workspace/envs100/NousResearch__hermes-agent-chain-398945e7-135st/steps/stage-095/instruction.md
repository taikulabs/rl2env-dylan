**fix(agent): try fallback providers at init when primary credential pool is exhausted (salvage #17958)**

When a provider has a single-key `credential_pool` and that key is in 429-cooldown, `resolve_provider_client` returns `None` and `AIAgent.__init__` used to raise a misleading `RuntimeError: no API key was found` — even when a valid `fallback_providers` chain was configured. This caused every fresh agent (cron jobs, new gateway sessions) to crash for the entire cooldown window, with the error suggesting the user set an env var that Hermes doesn't actually use for their provider.

## What changed
- `run_agent.py`: before raising the "no API key" `RuntimeError`, iterate `fallback_model` entries and call `resolve_provider_client` on each. If one resolves, adopt it as the effective primary, set `_fallback_activated=True`, and let the existing `_restore_primary_runtime` machinery promote the primary back once cooldown lifts. Preserves the flag across the later init block that used to reset it unconditionally.
- `tests/run_agent/test_init_fallback_on_exhausted_pool.py`: 2 tests — fallback adopted when primary returns None; original error preserved when no fallback is configured.

## Validation
- `scripts/run_tests.sh tests/run_agent/test_init_fallback_on_exhausted_pool.py` → 2 passed.
- `scripts/run_tests.sh tests/run_agent/` → 1192 passed (2 pre-existing failures unrelated to this change).
- E2E: three scenarios with real `AIAgent.__init__` and mocked `resolve_provider_client` —
  1. Primary exhausted + working fallback → agent comes up on fallback, `_fallback_activated=True`.
  2. Primary exhausted + no fallback → original `RuntimeError` preserved (message still names the provider and env var).
  3. Primary + first fallback both exhausted, second fallback working → chain walked through and agent adopts the second fallback.

.