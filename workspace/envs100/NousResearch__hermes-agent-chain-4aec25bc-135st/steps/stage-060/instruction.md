**fix(security): redact xAI (Grok) API keys in logs**

Salvage of #27349 by @flamiinngo cherry-picked onto current main.

## Summary
Adds the missing `xai-` prefix pattern to the log/output redactor so bare xAI API keys don't slip through into agent logs and tool output.

## Changes
- `agent/redact.py`: add `xai-[A-Za-z0-9]{30,}` to `_PREFIX_PATTERNS`
- `tests/agent/test_redact.py`: cover bare token, env assignment, too-short negative, company-name negative, prefix-preservation

## Validation
`scripts/run_tests.sh tests/agent/test_redact.py` → 80/80 passing.

 (salvage merge — author preserved).