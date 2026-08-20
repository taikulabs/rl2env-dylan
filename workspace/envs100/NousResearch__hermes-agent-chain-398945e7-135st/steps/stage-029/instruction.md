**fix(tools): serialize concurrent hermes_tools RPC calls from execute_code**

Salvages #17771 by @Heltman onto current `main`. . Also supersedes @vominh1919's #17872 (same fix, submitted 4h later — both contributors credited).

## Problem

Inside `execute_code`, concurrent tool calls from multiple threads (ThreadPoolExecutor, asyncio.to_thread, etc.) silently receive each other's responses. Responses are individually intact; they just get delivered to the wrong caller.

Root cause in `tools/code_execution_tool.py`:
- **UDS transport** (local backend) — `_sock` is a shared module-level connection, the newline-framed protocol has no request-id, the server handles requests serially in FIFO order, and `_call()` has no lock around `sendall + recv`. Concurrent callers race on `recv()` and get cross-matched.
- **File transport** (remote backends) — `_seq += 1` is a non-atomic read-modify-write, so two threads can allocate the same seq and clobber each other's request/response files.

## Fix (author: @Heltman, 2 files, +103/-17)

Smallest correct fix: wrap send+recv round-trip (UDS) and seq allocation (file) in a `threading.Lock`. No protocol change, no server change.

## Validation

```
scripts/run_tests.sh tests/tools/test_code_execution.py tests/tools/test_code_execution_modes.py
103 passed in 33.25s
```

New regression tests:
- `test_uds_transport_serializes_concurrent_calls` — asserts `_call_lock` is present in generated UDS source
- `test_file_transport_serializes_seq_allocation` — asserts `_seq_lock` is present in generated file source
- `test_concurrent_tool_calls_match_responses` — end-to-end: runs a sandboxed ThreadPoolExecutor of 10 `terminal()` calls with a slow mock dispatcher and asserts every caller sees its own tag (fails 10/10 without the fix).

## Backward compatibility

None broken. Single-threaded use is unchanged. The lock only affects concurrent callers inside one `execute_code` run — which were getting wrong answers without it. Server side is untouched.

Authorship preserved for @Heltman via plain

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_set_config_value.py`