**fix: STT provider-model mismatch — whisper-1 fed to faster-whisper**

## Summary

Legacy flat `stt.model` config key was causing `ValueError: Invalid model size 'whisper-1'` when users had the local (faster-whisper) STT provider configured. The gateway read the legacy key and passed it as a model override, bypassing provider-specific resolution.

## Root cause

- `cli-config.yaml.example` had a flat `stt.model: whisper-1` key (legacy format)
- Users who copied the example config got this key in their config.yaml
- Gateway called `get_stt_model_from_config()` which read the legacy flat key
- Passed `model='whisper-1'` to `transcribe_audio()` which used it as-is
- faster-whisper rejected it — it expects sizes like `base`, `small`, `large-v3`

## Changes

| File | Change |
|------|--------|
| `gateway/run.py` | Removed model override — `transcribe_audio()` handles it internally |
| `gateway/platforms/discord.py` | Same |
| `tools/transcription_tools.py` | Made `get_stt_model_from_config()` provider-aware; reads from correct nested section; ignores legacy flat key for local provider |
| `cli-config.yaml.example` | Updated STT section to nested provider config format |
| `hermes_cli/config.py` | Config migration v13→v14: moves legacy `stt.model` to correct provider section, removes flat key |
| `tests/` | Updated tests for new provider-aware behavior |