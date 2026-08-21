**fix: honor stt.enabled false across gateway transcription**

## Summary
- salvage the core gateway-side STT disable fix from PR #1110 onto current main
- bridge `stt.enabled` from `config.yaml` into `GatewayConfig` and skip gateway transcription cleanly when disabled
- add `stt.enabled` to the default user config and teach shared transcription helpers / voice-mode diagnostics to respect it too
- add regression coverage for config loading, disabled gateway transcription, and disabled STT provider selection

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_stt_config.py`
- `tests/tools/test_transcription.py`