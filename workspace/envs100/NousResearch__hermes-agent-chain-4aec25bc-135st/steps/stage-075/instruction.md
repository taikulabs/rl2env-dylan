**fix(conversation_loop): _ra()._pool_may_recover_from_rate_limit (NameError)**

Salvage of #28159 by @AceWattGit. Supersedes #28189, #28254, #28268 (all already-closed 1-line duplicates).

**What:** `agent/conversation_loop.py` line ~2335 called `_pool_may_recover_from_rate_limit(...)` bare, but the symbol was never imported in the file (it lives in `run_agent` and the rest of the module accesses it via the `_ra()` lazy loader). Any rate-limit fallback path hit `NameError: name '_pool_may_recover_from_rate_limit' is not defined`.

**How:** Route the call through `_ra()._pool_may_recover_from_rate_limit(...)` like every other run_agent symbol in this module, plus an inspect-based regression test that asserts the call site uses the namespace form (and that tests/monkeypatches on `run_agent` propagate correctly into the extracted loop).

Original PR: