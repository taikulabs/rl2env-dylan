**fix(agent): shrink anthropic-native image history**

## Summary
- Extends image-too-large retry recovery to Anthropic-native `image.source.base64` blocks, not only OpenAI-style `image_url` parts.
- Preserves the existing shrink gates for byte and dimension limits, including the many-image 2000px provider cap.
- Adds regression coverage for translated Anthropic base64 image history replay.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_image_shrink_recovery.py`