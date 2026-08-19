**fix(discord): voice session continuity and signal handler thread safety**

## Summary

Salvaged from PR #3475 by @twilwa. The Modal hosted gateway runtime portions were excluded — only the Discord voice session continuity fixes and signal handler thread safety guard are included.

### Changes

**Voice session continuity:**
- New `_voice_sources` dict stores `SessionSource.to_dict()` when `/voice channel` joins
- Voice input reuses the stored source metadata, keeping voice and text in the same session
- Voice-linked text channels get free-response treatment (skip @mention, skip auto-thread creation)
- Exemption scoped to exact channel ID — threads under the parent still require @mention
- `_voice_sources` cleaned up on `leave_voice_channel`

**Signal handler thread safety:**
- `start_gateway()` now checks `threading.current_thread() is threading.main_thread()` before registering signal handlers
- Prevents `RuntimeError` when the gateway runs in a non-main thread (e.g. daemon threads)

### Files changed (4 files, +130/-19)
- `gateway/platforms/discord.py` — `_voice_sources` dict, voice-linked channel detection, cleanup
- `gateway/run.py` — Source metadata storage on join, reuse on input, signal handler guard
- `tests/gateway/test_discord_free_response.py` — 2 new tests for voice-linked behavior
- `tests/gateway/test_voice_command.py` — Updated existing tests + new bound source reuse test

### Test results
- `test_discord_free_response.py` + `test_voice_command.py`: **165 passed**, 21 skipped
- Full `tests/gateway/`: **2686 passed**, 38 skipped (24 pre-existing failures unrelated to this change)

Credit: @twilwa for the original implementation in #3475.