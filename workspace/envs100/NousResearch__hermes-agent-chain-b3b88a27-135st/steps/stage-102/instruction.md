**fix(tui-gateway): dispatch slow RPC handlers on a thread pool**

## What does this PR do?

Fixes the single-threaded dispatcher freeze described in #12546. The `for raw in sys.stdin` loop in `tui_gateway/entry.py` calls `handle_request()` inline, so any handler that blocks for seconds to minutes — `slash.exec` (45s), `cli.exec` (up to 600s), `shell.exec` (30s), `session.resume` / `session.branch` (synchronous `_make_agent()`) — freezes the dispatcher. While one is running, inbound RPCs including `approval.respond` and `session.interrupt` sit unread in the stdin pipe buffer and only land after the slow handler returns.

This PR routes only those five handlers onto a small `ThreadPoolExecutor`; every other handler stays on the main thread. That's Option 2 from the issue — it gives us the user-visible responsiveness win without opening up the ordering / session-state race concerns that a full pool-everything refactor would.

## Related Issue