**fix(mcp): skip killpg when child shares gateway's process group**

## Summary

 — `/reload-mcp` crashes the gateway via a self-directed `killpg`.

`/reload-mcp` → `shutdown_mcp_servers` → `_kill_orphaned_mcp_children(include_active=True)` → `_send_signal` → `killpg(pgid, SIGTERM)` (`tools/mcp_tool.py`). When a tracked MCP stdio child shares the gateway's **own** process group, `killpg` delivers SIGTERM to the gateway itself, firing its SIGTERM handler → `os._exit(0)`. The gateway dies on plugin reload.

Verified still live on current `main` (`64131bf97`): `_send_signal` calls `killpg(pgid, sig)` unconditionally with no comparison against the gateway's own pgid.

## Fix

Pre-compute the gateway's own pgid (`os.getpgrp()`; `None` on Windows/restricted), and in `_send_signal` skip `killpg` when `pgid == own_pgid`, falling through to the per-pid `os.kill` path so the child is still reaped without self-signaling.

## Salvage / attribution

Salvaged from #47182 (@kyssta-exe), the cleanest of the #47134 cluster (single-file, focused, already approved — vs #47152 unreviewed-equivalent, #47142 conflicting+scope-creep, #47308 omnibus). Cherry-picked onto current `main`; authored by @kyssta-exe.

**Test added (folded in, co-authored):** the original PR shipped no regression test for the self-kill branch. Added `test_killpg_skipped_when_pgid_matches_gateway_own_pgroup`: with a tracked pgid equal to the gateway's own pgid, asserts `killpg` is never called for that pgid and the per-pid `kill` fallback is used. Mutation-checked (neutering the guard fails the test).

## Tests

`tests/tools/test_mcp_stability.py` — 22 pass (21 existing + the new self-kill-guard contract).