**fix(tui): reject /model and agent-mutating slash passthroughs while running**

## Summary
`agent.switch_model()` mutates 6+ agent attrs in place (`self.model`, `self.provider`, `self.base_url`, `self.api_key`, `self.api_mode`, plus rebuilds `self.client` / `self._anthropic_client`). The worker thread running `agent.run_conversation` reads those on every iteration. A concurrent `config.set` with `key=model` — or a slash-worker-mirrored `/model` / `/personality` / `/prompt` / `/compress` — can send an HTTP request with the new base_url but the old model (or vice versa), producing 400/404s the user never asked for.

Same race class as the `session.undo` / `session.compress` silent-drop (fixed in #12416) and the gateway runner's running-agent `/model` guard (fixed in #12334). Fix pattern matches.

## Changes
- `tui_gateway/server.py`:
  - `config.set` `key=model` returns 4009 `session busy` when `session.running` is True. Idle sessions switch normally.
  - `_mirror_slash_side_effects` rejects `/model` / `/personality` / `/prompt` / `/compress` with a `session busy` warning when running. Non-mutating passthroughs (e.g. `/queue`) still work.
- `tests/test_tui_gateway_server.py`: 4 regression cases.

## Validation
| | Before | After |
|---|---|---|
| `/model` via `config.set` mid-turn | mutates agent live — HTTP races | 4009 rejected, agent keeps running |
| `/model` via slash-worker passthrough mid-turn | same race | busy warning |
| `/personality` / `/prompt` / `/compress` via slash-worker passthrough mid-turn | same race | busy warning |
| Any of the above while idle | works | works (regression guard) |
| Non-mutating passthroughs (e.g. `/queue`) | works | works (unchanged) |

Regression-guard: against the unpatched `server.py`, the two `rejects_while_running` tests FAIL with the exact race message. With the fix, 4/4 pass.

Targeted: `test_tui_gateway_server.py` 41/41, `tests/tui_gateway/` 41/41 — 82 total.

Live E2E against the live Python environment:
```
=== Patch verification ===
  config.set model guard: OK
  slash-worker passthrough guard: OK
  slash mutating rejection: OK

=== E2E scenarios ===
  config.set model (running): error_code=4009  applied=0
  mirror '/model foo' (running):     busy-reject=True
  mirror '/personality bar' (running):     busy-reject=True
  mirror '/prompt' (running):     busy-reject=True
  mirror '/compress' (running):     busy-reject=True
  config.set model (idle):     result={'key': 'model', 'value': 'good/model', 'warning': ''}  applied=1
```