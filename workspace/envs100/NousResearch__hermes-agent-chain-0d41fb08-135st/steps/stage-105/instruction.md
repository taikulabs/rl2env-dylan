**fix(vision): auto-resize oversized images, raise limit to 20 MB, retry-on-failure**

## Summary

Salvaged from PR #7749 by @kshitijk4poor with modified strategy per Teknium's direction.

Fixes three independent bugs that compound into vision being completely broken on fresh installs (especially with Google/Gemini models).

## Changes

### 1. Raise hard image limit from 5 MB → 20 MB, retry-on-failure strategy
- **Old behavior:** Pre-resize all images to fit 5 MB before sending to API
- **New behavior:** Send images at full resolution (up to 20 MB). If the API rejects the image with a size-related error, auto-resize to 5 MB and retry once.
- `_MAX_BASE64_BYTES` = 20 MB (hard rejection limit, matches most restrictive major provider)
- `_RESIZE_TARGET_BYTES` = 5 MB (target for auto-resize on API failure)
- New `_is_image_size_error()` helper detects size-related API errors (413, too large, payload, etc.)
- Applied to both `vision_analyze_tool` (async) and `browser_vision` (sync)

### 2. Auto-resize with Pillow (soft dependency)
- Progressive downscaling: halve dimensions up to 4 rounds × reduce JPEG quality (85→70→50)
- PNG-aware: skips quality loop for PNGs (no effect)
- RGBA→RGB conversion for JPEG output
- File-size pre-check avoids expensive base64 encode for obviously huge files
- Graceful fallback when Pillow is not installed

### 3. Increase default vision timeout: 30s → 120s (`config.py`)
Both `vision_tools.py` and `browser_tool.py` had hardcoded fallbacks of 120s, but the config default of 30s always won. Now consistent.

### 4. Fix vision capability detection (`models_dev.py`)
`get_model_capabilities()` now checks both `attachment` flag AND `modalities.input` for `"image"`, consistent with `ModelEntry.supports_vision()`. Fixes models like gemma-4-31b-it being misdetected as non-vision.

## Tests
- 17 new tests: resize function (6), image size error detection (7), model capabilities (5), updated pre-existing size limit test (1)
- All 131 targeted tests pass

Credit: @kshitijk4poor (original PR #7749)