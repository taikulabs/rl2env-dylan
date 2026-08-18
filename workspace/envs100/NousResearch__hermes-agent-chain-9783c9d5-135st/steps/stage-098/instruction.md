**fix(terminal): preserve partial output when command times out**

When a command timed out in `_execute_oneshot`, all captured output was discarded — the agent only saw `Command timed out after Xs` with zero context about what happened. For long builds or test runs, this meant no way to tell which tests passed or where it failed.

The interrupt path (user sends a new message) already preserves partial output. The timeout path wasn't doing the same thing.

**E2E verified:**
- `echo line1 && echo line2 && sleep 30` (timeout=2) → all lines captured + timeout marker ✅
- `sleep 30` (timeout=1) → clean timeout message, no leading newline ✅
- 50-line output + sleep → all lines preserved + timeout marker ✅

Includes 2 regression tests from the original PR.

Salvaged from PR #3286 by @binhnt92 with authorship preserved.