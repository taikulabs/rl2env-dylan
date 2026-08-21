**fix(vision): reject non-image files and enforce website policy (salvage #1940)**

Salvage of #1940 by @GutSlabs. Cherry-picked cleanly with one test fix.

## Gaps fixed

| Issue | Before | After |
|-------|--------|-------|
| Local non-image files | Accepted by extension only — `secret.txt` renamed to `.png` would be sent to model | Magic-byte validation (PNG/JPEG/GIF/BMP/WebP/SVG headers) |
| Blocked URLs | No `check_website_access` in vision tool — blocked domains fetched freely | Policy check before download |
| Redirect bypass | Allowed URL → blocked redirect went through | Re-checks final URL after redirects |

## Test fix

One test needed `_validate_image_url` mocked — current main added `is_safe_url` DNS resolution checks that reject the fake `blocked.test` domain before the website policy check runs. The original PR predates that addition.

## Tests

6967 passed, 11 pre-existing failures, 0 regressions.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_vision_tools.py`