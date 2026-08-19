**feat: component-separated logging with session context and filtering**

## Summary

Addresses community request (Danny) for component-separated, filterable logging. Currently all three log files (agent.log, gateway.log, errors.log) receive identical records from the root logger — they're the same logs at different verbosity levels, not logs from different components.

### Phase 1 — Gateway log isolation
- `gateway.log` now only receives records from `gateway.*` loggers (platform adapters, session management, slash commands, delivery)
- `agent.log` remains the catch-all (everything goes there for correlation)
- `errors.log` remains WARNING+ catch-all
- Moved gateway.log handler creation from `gateway/run.py` into `hermes_logging.setup_logging(mode='gateway')` with a `_ComponentFilter`

### Phase 2 — Session ID injection
- Added `set_session_context(session_id)` / `clear_session_context()` API using `threading.local()` for per-thread session tracking
- `_SessionFilter` enriches every log record with a `session_tag` attribute
- Log format goes from: `2026-04-11 10:23:45 INFO gateway.run: msg`
- To: `2026-04-11 10:23:45 INFO [session_id] gateway.run: msg` (when session context is set)
- Session context set at start of `run_conversation()` in `run_agent.py`
- Thread-isolated: gateway conversations on different threads don't leak session IDs

### Phase 3 — Component filtering in `hermes logs`
- Added `--component` flag: `hermes logs --component gateway|agent|tools|cli|cron`
- `COMPONENT_PREFIXES` maps component names to logger name prefixes
- Works with all existing filters (`--level`, `--session`, `--since`, `-f`)
- Logger name extraction handles both old and new log formats

### Key design decisions
- **Zero changes to existing logger names** — `__name__` already provides the right hierarchy (`gateway.run`, `tools.terminal_tool`, `agent.context_compressor`, etc.)
- **Filter on handlers, not root logger** — Python logger filters skip propagated records from child loggers, so `_SessionFilter` is attached per-handler
- **Backward compatible** — `agent.log` format is identical for lines without session context; HUDs/parsers reading `agent.log` won't break