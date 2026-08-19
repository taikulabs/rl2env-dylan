**fix(xai-oauth): show 'not received' page when loopback callback has no code**

Salvage of #27439 by @briandevans 

## Summary
When xAI's auth backend fails to redirect and the user navigates to the bare loopback URL by hand, the callback handler previously returned a confusing 'authorization received' success page while the CLI was still waiting for a real callback and eventually timed out. Now returns a 400 with an explicit 'not received' page that tells the user to re-run `hermes auth add xai-oauth`.

## Changes
- `hermes_cli/auth.py`: early-return 400 + 'not received' page when both `code` and `error` are missing from the callback. Composes cleanly with the threaded server / first-wins latch added in #28110.
- `tests/hermes_cli/test_auth_xai_oauth_provider.py`: 3 new tests (bare URL → 400, code+state → 200, error param → 200).

## Validation
`scripts/run_tests.sh tests/hermes_cli/test_auth_xai_oauth_provider.py` → 68/68 passing (covers both #27420 latch behavior and #27439 not-received behavior).

, #27385 (salvage merge — author preserved).