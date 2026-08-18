**feat(tools): add Voxtral TTS provider (Mistral AI)**

## Summary

Cherry-pick salvage of PR #6301 by @jjovalle99 (Mistral AI).

Adds Mistral's Voxtral TTS as a sixth text-to-speech provider. Companion to the already-merged Voxtral STT from the same contributor.

**Config:** `tts.provider: mistral` + `MISTRAL_API_KEY`

## Changes

- `tools/tts_tool.py`: `_generate_mistral_tts()`, base64 audio decoding, format mapping (.ogg→opus, .wav, .flac, .mp3)
- `tests/tools/test_tts_mistral.py`: 17 tests covering generation, format mapping, voice IDs, error sanitization, dispatch, Telegram Opus path
- `hermes_cli/config.py`: default TTS config for mistral (model + voice_id) + `MISTRAL_API_KEY` in OPTIONAL_ENV_VARS
- `hermes_cli/setup.py`: mistral added to TTS provider selection wizard
- `hermes_cli/tools_config.py`: mistral added to TTS provider list
- `hermes_cli/nous_subscription.py`: TTS label and availability check
- `scripts/discord-voice-doctor.py`: mistral config validation
- Docs: tts.md, providers.md, voice guide, config example

## Highlights

- Native Opus output for Telegram voice bubbles — no ffmpeg conversion needed
- Reuses existing `mistralai` SDK dependency from the STT merge
- Also adds `MISTRAL_API_KEY` to `OPTIONAL_ENV_VARS` (was missing from STT merge)

## Test Results

- 17/17 Mistral TTS tests pass
- 135/135 targeted tests pass (TTS, transcription, tools_config)

. Supersedes #6301 — contributor's commit cherry-picked with authorship preserved.