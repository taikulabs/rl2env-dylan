**feat(tts): add Google Gemini TTS provider**

## Summary

Adds Google Gemini TTS as the seventh voice provider in the TTS tool — driven by the Shubham Saboo / OpenClaw mention. 30 prebuilt voices (Zephyr, Puck, Kore, Enceladus, Gacrux, etc.) with natural-language prompt control (`say cheerfully:`, inline `[whispers]` tags).

Integrates cleanly through the existing provider chain — no new SDK dep, uses raw REST like xAI/MiniMax.

## What changed

| File | Change |
|---|---|
| `tools/tts_tool.py` | New `_generate_gemini_tts()` + `_wrap_pcm_as_wav()`; routed in main dispatcher; `check_tts_requirements()` accepts `GEMINI_API_KEY` / `GOOGLE_API_KEY` |
| `hermes_cli/tools_config.py` | 'Google Gemini TTS' entry added to the `hermes tools` TTS picker |
| `hermes_cli/setup.py` | Wizard picker, status display, and API-key prompt branch |
| `tests/tools/test_tts_gemini.py` | 15 unit tests (WAV header, env fallback, voice/model overrides, snake_case inlineData, HTTP error surfacing, etc.) |
| `website/docs/user-guide/features/tts.md` | Provider table, config example, ffmpeg notes |

## Design notes

- **REST over SDK.** No `google-genai` dependency added — mirrors xAI/MiniMax raw-request pattern. Keeps the install footprint small.
- **PCM → WAV wrap → ffmpeg.** Gemini returns raw L16 PCM @ 24kHz mono 16-bit (no container). A 44-byte WAV RIFF header is prepended, then ffmpeg encodes to MP3 / Opus depending on the output extension.
- **Telegram-compatible Opus.** For `.ogg` output we explicitly pass `-acodec libopus` (ffmpeg defaults to Vorbis for `.ogg`, which Telegram doesn't show as a voice bubble). Same `-b:a 64k -ac 1` settings as the existing `_convert_to_opus` helper.
- **Key fallback.** Accepts either `GEMINI_API_KEY` (primary) or `GOOGLE_API_KEY` (same key, different env name).
- **New key format tolerance.** Google has rolled out a new key format (`AQ.Ab8R…` instead of `AIza…`); both work transparently against `/v1beta/generateContent`.