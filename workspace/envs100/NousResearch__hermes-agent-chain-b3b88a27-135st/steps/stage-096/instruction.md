**fix(telegram): salvage docker-only MEDIA path diagnostics**

## Summary
- salvages helix4u's Telegram/Docker MEDIA path diagnostics from #6392 onto current main
- preserves the original contributor commit and adds a small current-main follow-up commit
- improves both runtime diagnostics and docs for Docker-backed gateway file delivery

## What this fixes
When the agent emits `MEDIA:/...` paths from a Docker-backed terminal, the gateway process runs on the host and cannot read container-local paths like `/workspace/report.txt`.

Current main only says `File not found: ...`, which hides the real problem.

This salvage adds:
- clearer Telegram local-media errors when MEDIA points at container-local paths
- a gateway startup warning when Docker-backed messaging has no explicit host-visible export mount
- docs/config examples for the recommended host-visible export pattern
- focused regression tests

## Tightening added on top of the original PR
Current-main follow-up fixes included in this salvage:
- reuse one helper for the Docker-local path hint across document/image/video/audio local-media send paths
- include `/outputs/...` alongside `/output/...`
- soften the startup warning so it does not falsely imply custom host-visible mounts are broken; it now warns specifically about the risky container-local MEDIA path pattern
- add extra regressions for `/outputs/...` and non-document media coverage

## Files changed
- `gateway/platforms/telegram.py`
- `gateway/run.py`
- `hermes_cli/config.py`
- `tests/gateway/test_runner_startup_failures.py`
- `tests/gateway/test_telegram_documents.py`
- `website/docs/user-guide/configuration.md`
- `website/docs/user-guide/messaging/telegram.md`

## Verification
Focused tests:
- `python -m pytest tests/gateway/test_telegram_documents.py tests/gateway/test_runner_startup_failures.py -o "addopts=" -q`
- result: `42 passed`

Syntax/smoke:
- `python3 -m py_compile gateway/run.py`
- `python3 -m py_compile gateway/platforms/telegram.py`
- `python3 -m py_compile tests/gateway/test_runner_startup_failures.py`
- `python3 -m py_compile tests/gateway/test_telegram_documents.py`

## Contributor credit
This PR