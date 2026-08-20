**fix(security): extend secret redaction to ElevenLabs, Tavily and Exa API keys**

ElevenLabs (`sk_`), Tavily (`tvly-`), and Exa (`exa_`) API keys were not covered by `_PREFIX_PATTERNS` in `agent/redact.py`, leaking in plain text via `printenv` or log output.

**E2E verified** — all three key types now fully redacted in env dumps, log lines, and inline text. Non-secret lines preserved. Existing Stripe patterns unaffected.

Tests rewritten with correct assertions — the original PR's tests used vacuously true checks (`assert 'abc123def456' not in result` where that string was never in the input).

Salvaged from PR #3790 by @memosr with authorship preserved.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_redact.py`