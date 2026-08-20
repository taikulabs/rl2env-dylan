**fix(moonshot): strip null-type anyOf branches + null/empty enum values (salvages #18177)**

MCP tools with `anyOf: [{enum: [...]}, {type: null}]` shapes no longer 400 on Kimi/Moonshot. Salvages @hendrixfreire's PR #18177 with a follow-up bug fix.

## What changed
- `agent/moonshot_schema.py`: reorder Rule 1 before Rule 3 so enum cleanup has a type to check; new Rule 3 strips `null` / `""` from enum arrays on scalar types; strip non-standard `nullable` keyword; collapse `anyOf` null-type branches to the single non-null branch.
- Follow-up: when the anyOf collapse produces a single merged node, fall through to Rules 1/3 instead of early-returning — otherwise the merged node keeps `nullable` and bad enum values, and Moonshot still rejects it.
- +34 tests in `tests/agent/test_moonshot_schema.py` covering every shape.

## Root cause
PR #14805 landed a Moonshot schema sanitizer, but did not cover three Moonshot rejection modes: null-type branches inside `anyOf`, null/empty-string inside `enum` arrays, and the non-standard `nullable` keyword. Real MCP schemas (dataslayer `db_type`, others) hit all three.

## Validation
| | Before | After |
|---|---|---|
| dataslayer `db_type` anyOf+enum | HTTP 400 | accepted, enum=[mysql,mariadb,…] |
| anyOf [scalar, null] with parent `nullable` | `nullable` leaked through | stripped |
| Regression — ordinary schemas | pass | pass |
| Test suite `tests/agent/test_moonshot_schema.py` | 26 | 34 (all pass) |

.
Salvages #18177 — @hendrixfreire's commit cherry-picked with authorship preserved via rebase-merge.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_moonshot_schema.py`