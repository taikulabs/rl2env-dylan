**fix(agent): route compression auxiliary using live session model instead of stale persisted config**

## Summary

Salvage of #8146 by @counterposition — cherry-picked onto current main.

After a session-only `/model` switch (without `--global`), compression auxiliary auto-routing continued reading the main model and provider from persisted `config.yaml` instead of the live in-memory session values. This meant compression feasibility checks and summary generation could route through a stale backend.

Most visible when `config.yaml` persists a small-context model (e.g. `glm-5.1`) while the session switches to a large-context model (e.g. `gpt-5.4`): compression would warn or error based on the old model's context window.

### What changed

- Thread an optional `main_runtime` dict through auxiliary auto-routing in `auxiliary_client.py`
- Compression feasibility checks now pass the live runtime from the active agent session
- `ContextCompressor` passes the live runtime into compression summary `call_llm()` calls
- Explicit `auxiliary.compression` pinning in config remains authoritative over live runtime
- Include the live runtime in auto-client cache keys so session-only switches don't reuse stale cached clients
- Add `api_mode` to `ContextCompressor.__init__` and `update_model()` (was missing)

### Tests

6 targeted tests covering:
- Auto-routing prefers live runtime over persisted config
- Explicit compression pin still wins over live runtime
- Summary generation passes live runtime to `call_llm`
- Feasibility check passes live runtime to auxiliary client