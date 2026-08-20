**feat(providers): add native xAI provider**

Adds xAI as a first-class provider. ProviderConfig, HermesOverlay, 11 curated Grok models, URL mapping, aliases, tests. Standard OpenAI-compatible — no adapter needed. 127 provider tests passing. Salvaged from #7050, contributor authorship preserved (@Julientalbot).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_api_key_providers.py`