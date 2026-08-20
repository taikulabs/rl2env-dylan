**fix: handle gateway Ctrl+C shutdown cleanly**

## Summary
- catch `KeyboardInterrupt` around foreground gateway startup so `hermes gateway` exits cleanly on Ctrl+C
- print a short shutdown message instead of surfacing the asyncio traceback
- add regression coverage for both Ctrl+C shutdown and the existing nonzero failure path

## Verification
- `scripts/run_tests.sh tests/hermes_cli/test_gateway.py -q`
- `scripts/run_tests.sh tests/hermes_cli/test_gateway.py tests/hermes_cli/test_gateway_service.py -q`
- independent reviewer pass via delegation (no security or logic issues found)

Followed `CONTRIBUTING.md` and `AGENTS.md`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_gateway.py`