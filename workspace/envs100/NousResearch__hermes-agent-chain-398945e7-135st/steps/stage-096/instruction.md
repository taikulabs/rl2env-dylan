**feat: add video_analyze tool for native video understanding**

## Summary

Adds a `video_analyze` tool that sends video files to multimodal LLMs (e.g. Gemini) via the OpenRouter `video_url` content type for native video understanding — no frame extraction, no ffmpeg dependency.

Mirrors `vision_analyze` in structure: same error handling, SSRF protection, retry logic, cleanup, and registration pattern.

## Design

- **API format:** `video_url` content block with base64 data URL (`data:video/mp4;base64,...`)
- **Formats:** mp4, webm, mov, avi, mkv, mpeg
- **Size limits:** 50 MB hard cap, 20 MB warning
- **Timeout:** 180s floor (videos take longer than images)
- **Model override:** `AUXILIARY_VIDEO_MODEL` env → `AUXILIARY_VISION_MODEL` fallback → auxiliary vision config
- **Toolset:** `video` (default disabled — NOT in `_HERMES_CORE_TOOLS`)

## Enabling

```bash
hermes tools enable video
# or in config.yaml: agent.enabled_toolsets: [video]
# or per-session: enabled_toolsets=['video']
```

## Files Changed

- `tools/vision_tools.py` — `video_analyze_tool` + `VIDEO_ANALYZE_SCHEMA` + registry
- `toolsets.py` — `"video"` toolset definition
- `tests/tools/test_video_analyze.py` — 29 tests (MIME detection, base64, schema, handler, integration, registration)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_video_analyze.py`