**refactor: unify vision backend gating**

## Summary
- unify vision backend availability behind a single runtime resolver
- stop treating vision as effectively OpenRouter-only in setup and tools config
- make Codex, Nous, and custom OpenAI-compatible backends count consistently for vision tool availability

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_setup_model_provider.py`
- `tests/hermes_cli/test_tools_config.py`
- `tests/tools/test_vision_tools.py`