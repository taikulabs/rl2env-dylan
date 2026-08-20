**fix(gateway): detect script-style gateway processes for --replace**

Adds `hermes_cli/main.py gateway` to the recognized process-detection patterns in `_looks_like_gateway_process()`, `_record_looks_like_gateway()`, and `find_gateway_pids()`. Without this, `--replace` fails to detect gateway instances started via script-style invocations, allowing duplicate instances that produce duplicate Discord replies.

Includes regression test. All 9 status tests pass.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_status.py`