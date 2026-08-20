**fix: restore local STT fallback for gateway voice notes**

## Summary
- restore local STT command fallback for voice transcription, including auto-detecting local whisper and ffmpeg in common install paths
- let OpenAI STT fall back to OPENAI_API_KEY and prefer local fallback before cloud-only failure messaging
- avoid bogus Telegram/gateway "no STT provider configured" text when the actual failure is a backend-specific key problem
- document the local STT fallback env vars and updated provider behavior

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_stt_config.py`
- `tests/tools/test_transcription_tools.py`