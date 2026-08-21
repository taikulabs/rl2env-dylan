**fix(custom-endpoint): verify /models and suggest working /v1 base URL**

## Summary
- add real `/models` verification for custom OpenAI-compatible endpoints in both `hermes setup` and `hermes model`
- probe a light `/v1` fallback when the user enters a base URL without `/v1`, and save the verified working base URL when that fallback succeeds
- improve custom-endpoint validation warnings so Hermes shows the exact URL it probed and suggests a likely `/v1` correction instead of silently accepting an unverifiable endpoint

## Why this addresses #1460
The issue mixed two different failure modes:
1. setup/model configuration gave almost no feedback about whether the entered endpoint was reachable or what exact URL Hermes would probe
2. users were left guessing whether their server wanted `http://host` or `http://host/v1`

This PR fixes the Hermes-side configuration/verification gap. It does not assume every downstream server bug is Hermes' fault, but it makes the base URL behavior explicit and immediately testable.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_model_validation.py`
- `tests/hermes_cli/test_setup_model_provider.py`
- `tests/test_cli_provider_resolution.py`