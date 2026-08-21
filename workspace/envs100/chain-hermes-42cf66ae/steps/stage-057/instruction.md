**fix: smart vision setup that respects the user's chosen provider**

## Summary
- salvage the provider-aware vision setup flow from #945 onto current main
- make the setup summary report vision availability for OpenRouter, active Nous/Codex auth, and direct OpenAI endpoints instead of hardcoding OPENROUTER_API_KEY
- keep the OpenAI vision default explicit so auxiliary vision uses gpt-4o-mini instead of falling back to the main model slug
- add regression coverage for the new vision prompts and summary behavior

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_setup_model_provider.py`