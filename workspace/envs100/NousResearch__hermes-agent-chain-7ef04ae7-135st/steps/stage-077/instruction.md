**fix(security): redact Fireworks AI API keys in logs**

## Summary
Raw Fireworks AI API keys now get masked in logs, stack traces, and tool output. Fireworks is a registered provider (`FIREWORKS_API_KEY` is passed to the agent environment in `tools/environments/local.py` and listed in `hermes_cli/models.py`), but its `fw_<40 alnum>` key format was missing from `_PREFIX_PATTERNS` in `agent/redact.py` — only the `FIREWORKS_API_KEY=...` env-assignment form was caught, so a bare key in a traceback or debug print leaked verbatim.

## Changes
- `agent/redact.py`: add `r"fw_[A-Za-z0-9]{30,}"` to `_PREFIX_PATTERNS`. The 30-char minimum matches the real 40-char keys while guarding short false positives like `fw_version`. `fw_` extracts cleanly as a literal prefix-substring, so the `_PREFIX_SUBSTRINGS` pre-screen stays correct.
- `tests/agent/test_redact.py`: `TestFireworksToken` — bare token masking, env-assignment masking, short-prefix false-positive guard, visible-prefix-in-output.

## Validation
| | Before | After |
|---|---|---|
| `fw_…` in a stack trace | leaked verbatim | masked (`fw_AA…`) |
| `fw_version` short string | n/a | left untouched |
| redact suite | — | 126/126 pass |

Salvaged from #27500 by @flamiinngo via cherry-pick (authorship preserved). E2E-verified with real imports against the live redactor.

## Infographic
![Redact Fireworks AI keys](https://v3b.fal.media/files/b/0aa05c32/hBJiFG24Qs26b2FDVm2wv_p4G3oFs1.png)

— Nous Research

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_redact.py`