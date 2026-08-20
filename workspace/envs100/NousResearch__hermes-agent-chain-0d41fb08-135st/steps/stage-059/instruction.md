**fix(model_metadata): add xAI Grok context length fallbacks**

## Summary

xAI's `/v1/models` endpoint does not return `context_length` metadata. Users pointing at `https://api.x.ai/v1` via a custom provider fall through to the 128k probe-down default, losing up to 93% of the usable window (e.g. 128k instead of 2M for grok-4.20).

Adds `DEFAULT_CONTEXT_LENGTHS` entries for the Grok family — same pattern as Claude, Gemma, MiniMax, Kimi, and GLM.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_model_metadata.py`