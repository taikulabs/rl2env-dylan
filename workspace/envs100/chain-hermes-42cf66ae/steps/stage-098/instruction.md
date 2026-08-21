**fix: harden ClawHub skill search exact matches**

## Summary
- harden the ClawHub Skills Hub adapter so exact slug searches can recover when ClawHub search returns irrelevant results
- repair poisoned cached search results by re-checking an exact slug lookup on read
- parse nested `skill` payloads from the ClawHub detail endpoint so direct inspect fallback returns real metadata
- normalize ClawHub tag dictionaries into usable tag lists
- add regression coverage for irrelevant search results, poisoned cache recovery, and nested detail payloads

## Why
`hermes skills search self-improving-agent --source clawhub` was reaching ClawHub, but the ClawHub search endpoint was returning unrelated skills for that exact query. The skill was still directly accessible at `/api/v1/skills/self-improving-agent`, so Hermes needed a stricter exact-match fallback instead of trusting the noisy search response.

## Validation
Working locally after the fix:
- `python -m hermes_cli.main skills search self-improving-agent --source clawhub`
- result now surfaces `self-improving-agent` as the exact ClawHub hit

Tests run:
- `python -m pytest tests/tools/test_skills_hub_clawhub.py tests/tools/test_skills_hub.py tests/hermes_cli/test_skills_hub.py -n0 -q`
- `python -m pytest tests/ -n0 -q`

Note on full suite:
- current main still has two unrelated failing tests:
  - `tests/test_api_key_providers.py::TestResolveProvider::test_auto_detects_minimax_cn_key`
  - `tests/test_openai_client_lifecycle.py::test_concurrent_requests_do_not_break_each_other_when_one_client_closes`
- those failures reproduce outside the ClawHub changes; the targeted Skills Hub tests pass cleanly.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_skills_hub_clawhub.py`