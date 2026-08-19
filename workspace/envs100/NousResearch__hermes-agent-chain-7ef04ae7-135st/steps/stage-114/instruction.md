**fix(security): constrain persisted tool-result filenames to their storage dir**

## Summary
A model/provider-supplied tool-call id can no longer escape the persisted-result storage directory — the id is normalized to a single safe filename segment before the path is built.

Root cause: `agent/tool_executor.py` passes `tool_call.id` (model/provider-controlled) straight into `f"{storage_dir}/{tool_use_id}.txt"`. The existing `shlex.quote` (PR #7912) blocks shell metacharacters but is orthogonal to path-segment containment — a quoted `/tmp/hermes-results/../../etc/cron.d/x.txt` is still a valid path that resolves outside the storage dir, so an id like `../../etc/cron.d/x` writes attacker content to an arbitrary location.

## Changes
- `tools/tool_result_storage.py`: add `_safe_result_filename()` (collapse unsafe chars → `_`, strip leading/trailing dots, hash-suffix when changed or over length) and route the persisted path through it. Single chokepoint — the budget-enforcement path feeds back through `maybe_persist_tool_result`, so it's covered transitively.
- `tests/tools/test_tool_result_storage.py`: regression coverage for normal-id preservation and traversal/metacharacter containment.

## Validation
| input | before | after |
|---|---|---|
| `tc_456` | `tc_456.txt` | `tc_456.txt` (unchanged) |
| `../../etc/cron.d/x` | escapes `/tmp/hermes-results` | `etc_cron.d_x_<hash>.txt` (contained) |
| `..` / empty / `None` | traversal / odd paths | `tool_result(_<hash>).txt` |

`scripts/run_tests.sh tests/tools/test_tool_result_storage.py` → 52 passed. E2E'd all attack vectors: every output is a contained single segment; legit ids unchanged.

Salvaged from #10097 (@WuKongAI-CMU), 

## Infographic

![infographic](https://v3b.fal.media/files/b/0aa06d71/upt3P_duyDw2Cv_aNYOBV_SMVDnpDi.png)