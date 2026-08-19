**feat(gateway): periodic memory logging for leak detection (salvage of #17667)**

## Summary
Salvage of #17667 — gateway daemon thread logs `[MEMORY] rss=...MB gc=... threads=... uptime=...s` to `gateway.log` every 5 minutes so slow leaks in the long-lived process show up as a time series. Port from cline/ (`src/standalone/memory-monitor.ts`).

Hermes has a `memory-leak-audit` skill and the gateway caches agent instances, session transcripts, MCP connections, tool schemas, and memory providers — exactly the kind of long-running process where a leak in any one subsystem is invisible until you watch RSS climb for hours.

## Adaptation vs. the TS upstream
- Node `setInterval` + `.unref()` → Python `threading.Thread(daemon=True)` driven by `threading.Event.wait()` so shutdown is immediate instead of waiting for the next tick.
- Log line includes `gc=(gen0,gen1,gen2)` and `threads=N` instead of V8's `external` / `arrayBuffers` — more useful for Python leaks (thread leaks + GC pressure are the common gateway failure modes).
- No Node `--heapsnapshot-near-heap-limit` equivalent. CPython's closest analogue is `tracemalloc`, which has non-trivial steady-state overhead; deferred unless someone asks.
- Config-gated under `logging.memory_monitor.enabled` (default true), matching other diagnostic toggles.

## Changes
- `gateway/memory_monitor.py` (+232): functional API — `start_memory_monitoring()`, `stop_memory_monitoring()`, `log_memory_usage()`. Uses `resource.getrusage()` (stdlib, Linux/macOS) first, falls back to `psutil` (already an optional dep via `mcp_tool.py`), disables itself with one WARNING if neither works.
- `gateway/run.py` (+20): wired into startup right after `setup_logging()`, stop alongside `shutdown_mcp_servers()`. Wrapped in best-effort try/except so a monitor failure can never break gateway startup.
- `hermes_cli/config.py` (+5): new `logging.memory_monitor` block (enabled: true, interval_seconds: 300).
- `tests/gateway/test_memory_monitor.py` (+141): 10 targeted unit tests.

## Validation
| | Result |
|---|---|
| `tests/gateway/test_memory_monitor.py` | 10/10 |
| `tests/gateway/` (regression) | 5506/5506 |
| E2E (real `start_memory_monitoring(0.3s)` smoke run) | baseline + periodic + shutdown lines all emit; RSS, GC, threads, uptime all populated |

Sample output:
```
[MEMORY] baseline rss=25MB gc=(1082, 5, 1) threads=1 uptime=0s
[MEMORY] Periodic memory monitoring started (interval: 0s)
[MEMORY] rss=25MB gc=(1125, 5, 1) threads=2 uptime=0s
[MEMORY] shutdown rss=25MB gc=(1129, 5, 1) threads=2 uptime=0s
[MEMORY] Periodic memory monitoring stopped
```

Quick "RSS over time" view:
```bash
grep '\[MEMORY\] rss=' ~/.hermes/logs/gateway.log | awk '{print $1,$2,$4}'
```

## Source
cline/. Originally scouted in #17667.