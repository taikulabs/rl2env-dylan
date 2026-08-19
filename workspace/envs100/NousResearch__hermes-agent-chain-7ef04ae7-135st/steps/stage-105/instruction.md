**fix(gateway): deliver extension-less MEDIA files + strip [[as_document]] guard**

## Summary
Extension-less `MEDIA:` files (Caddyfile, Dockerfile, Makefile) now deliver as native attachments on the gateway instead of leaking the raw `MEDIA:/path/Caddyfile` line to the user as text.

Root cause: both `extract_media` and `extract_local_files` required a known file extension, so a bare extension-less path matched neither extractor — the tag was never extracted and stayed visible in the message body.

Salvage of #55702 by @HexLab98, cherry-picked onto current `main` with authorship preserved, plus a follow-up fix for the review note Gille raised.

## Changes
- `gateway/platforms/base.py`: new `MEDIA_EXTENSIONLESS_TAG_RE` + helpers extract extension-less `MEDIA:` paths, gated by `validate_media_delivery_path` so an injection path that isn't on disk / outside allowed roots stays visible rather than being delivered. Shared display-strip logic (`strip_media_directives_for_display`).
- `gateway/stream_consumer.py`: streaming display cleanup now delegates to the shared base.py logic (one definition, both paths behave identically).
- **Follow-up fix:** the extension-less guards short-circuited on `"MEDIA:" not in text and "[[audio_as_voice]]" not in text`, so a response carrying only `[[as_document]]` (image-only reply requesting unmodified document delivery) leaked the directive as visible text. Added `[[as_document]]` to both guard conditions + a regression test.

## Validation
| | Before | After |
|---|---|---|
| `MEDIA:/output/Caddyfile` on Telegram | raw text leaks | delivered as attachment |
| `MEDIA:/nonexistent/Dockerfile` (injection) | n/a | stays visible, not delivered |
| `[[as_document]]` with no MEDIA: tag | leaked as text | stripped |
| `.md`/`.json`/known-ext delivery | works | unchanged |

- `scripts/run_tests.sh tests/gateway/test_platform_base.py tests/gateway/test_media_extraction.py tests/gateway/test_stream_consumer.py` → 291 passed, 0 failed.
- E2E with real file I/O (temp HERMES_HOME, real Caddyfile on disk, allowed-root config): Caddyfile delivers, injection path blocked, `[[as_document]]` stripped at both entry points, plain text untouched.

## Infographic
![MEDIA extension-less file delivery](https://v3b.fal.media/files/b/0aa06ac3/okXi81oXzp60VkoRoF7ew_xXNGJBWx.png)