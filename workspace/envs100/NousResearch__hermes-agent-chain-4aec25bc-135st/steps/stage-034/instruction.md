**fix(api_server): coerce stringified booleans in stream/store/approval payloads (salvage #26639)**

## Summary
Salvage of #26639 — OpenAI-compatible clients that send booleans as strings (e.g. `"stream": "false"`) had those values evaluated with Python truthiness, so `"false"` was treated as `True`. Routed `/v1/chat/completions` and `/v1/responses` into SSE mode, made `store="false"` actually store, and let `all="false"` fan out approvals across the queue.

## Changes
- `gateway/platforms/api_server.py` — add `_coerce_request_bool()` helper, apply to `stream`, `store`, and `all`/`resolve_all` payload fields.
- `tests/gateway/test_api_server*.py` — four regression tests for `stream: "false"`, `store: "false"` (responses), and `all: "false"` (run approval).

## Validation
- `scripts/run_tests.sh tests/gateway/test_api_server.py tests/gateway/test_api_server_runs.py -q` → 171/171 pass.

Coercion handles real bool, `None` → default, `"1"/"true"/"yes"/"on"` → True, `"0"/"false"/"no"/"off"` → False, ints/floats via `bool()`. Anything else falls back to caller's default.

Original PR: #26639 — credit preserved via rebase-merge.