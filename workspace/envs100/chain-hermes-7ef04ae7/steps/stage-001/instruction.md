**fix(dashboard): close PTY WebSocket on child EOF to stop FD leak**

## Summary
Dashboard `/chat` PTY sessions no longer leak file descriptors when the browser socket drops uncleanly.

Root cause: the `/api/pty` reader task returns on child EOF, but the writer loop stayed blocked on `ws.receive()` until the browser sent a disconnect. When the browser socket is half-open (no FIN delivered — common on macOS/launchd), that disconnect never arrives, so the handler never reaches its `finally` and the PTY master fd + child process leak. Dashboard auto-reconnect then spawns a fresh PTY on every dropped socket, stacking on the orphaned one until the gateway hits `EMFILE` (Errno 24) within hours.

## Changes
- `hermes_cli/web_server.py`: the `pump_pty_to_ws` reader task now closes the WebSocket in a `finally` when the child EOFs or the send side breaks. That unblocks the writer's `ws.receive()` so the existing `finally` runs `bridge.close()` and reaps the PTY. The writer loop guards `ws.receive()` against the `RuntimeError` Starlette raises once the socket is already closed.
- `tests/hermes_cli/test_web_server_pty_reconnect.py`: regression test — a client that reads one frame and never disconnects must still see the server tear down the socket and reap the bridge on child EOF.

## Validation
| | Before fix | After fix |
|---|---|---|
| Child EOF, half-open client socket | handler blocks in `ws.receive()` forever; PTY fd + child leak | server closes WS → `bridge.close()` runs |
| New regression test | hangs (60s timeout) | passes in <1s |
| `test_web_server_pty_reconnect.py` | — | 4 passed |

Reported by @fifteenzhang.

## Infographic

![PTY WebSocket FD leak fix](https://v3b.fal.media/files/b/0aa01715/pYp5Nn8XcxInN63AxBMMR_2sSvVlja.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_web_server_pty_reconnect.py`