**fix(signal): back off sendTyping spam for unreachable recipients**

## Summary
Signal `send_typing` backs off after repeated NETWORK_FAILUREs so an unreachable recipient stops producing a WARNING log every 2 seconds for as long as the agent is busy.

## Problem
`base.py::_keep_typing` refreshes the typing indicator every ~2s while the agent processes a turn. When signal-cli returns NETWORK_FAILURE (recipient offline, unroutable, group membership lost), the unmitigated `_rpc` path logs WARNING on every single refresh. A user report showed **1048 warnings in 41 minutes** for one offline contact, with a matching volume of pointless RPC traffic to signal-cli.

## Changes
| File | What |
|---|---|
| `gateway/platforms/signal.py` | `_rpc()` takes `log_failures: bool = True`; `send_typing()` tracks consecutive failures per chat and short-circuits the RPC during an exponential cooldown (16s → 32s → 60s cap) after 3 failures; first failure still logs WARNING, subsequent ones log DEBUG; success resets counters; `_stop_typing_indicator()` clears the backoff state |
| `tests/gateway/test_signal.py` | `TestSignalTypingBackoff` — 5 tests covering log-level demotion, 3-failure cooldown engagement, per-chat isolation, success reset, stop-typing cleanup |

## Validation
| | Before | After |
|---|---|---|
| RPCs in 41-min offline window | 1230 | 45 (-96%) |
| WARNING log lines | 1048 | 1 |
| DEBUG log lines | 0 | 44 |
| `tests/gateway/test_signal.py` | 57 passed | 62 passed |

E2E simulation replays `base.py::_keep_typing` calling `send_typing` every 2s for the reported 41-minute duration against a stub `_rpc` that returns the exact NETWORK_FAILURE shape from the user's log.

## Notes
Salvages the `_rpc(log_failures=...)` kwarg idea from #12056 (credits @kshitijk4poor). The broader restructure in that PR — a second nested per-chat loop inside `send_typing` interacting with base.py's `_keep_typing` via asyncio.Task cleanup — is avoided here in favour of stateful backoff that preserves the existing `_keep_typing` architecture. Closing #12056 in favour of this narrower fix; the session_search serialization half of that PR is unrelated to the reported incident (logs show aux timeouts, not 429s) and isn't included here.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_signal.py`