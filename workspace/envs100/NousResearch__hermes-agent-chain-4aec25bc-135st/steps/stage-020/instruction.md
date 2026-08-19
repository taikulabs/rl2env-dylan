**fix(moonshot): strip $ref siblings and collapse tuple items in tool schemas (salvage of #18130)**

## Summary
Salvage of #18130 — closes two HTTP 400 bypasses on Moonshot/Kimi:
1. MCP-sourced tool schemas with `$ref` + sibling `description` (MCP tools put a description on `$ref`-typed properties so the model sees the field hint).
2. Tuple-style `items` arrays (common in Go/Protobuf-generated schemas).

Both worked on every other provider; Moonshot's validator expands `$ref` before checking siblings, and refuses tuple `items` outright.

Port from anomalyco/.

## Salvage notes
Branch was 1,676 commits stale. One conflict in `agent/moonshot_schema.py`: main added an enum-null cleanup pass between the PR's branch point and now (its own Rule 3). Resolution: kept main's enum rule, renumbered — enum→Rule 3, $ref-sibling→Rule 4, tuple-items→Rule 5. Docstring + class docstrings updated to match.

One test adjustment: `test_ref_inside_anyof_children` originally expected the `anyOf` wrapper to survive. Main's existing anyOf-with-null collapse (Rule 2) now promotes the single non-null branch to the parent. Rule 4 then strips the sibling, leaving exactly `{"$ref": "..."}` at the property level — semantically equivalent but tighter. Updated the assertion to match.

## Changes
- `agent/moonshot_schema.py` (+19/-3): new Rule 4 (`$ref` sibling stripping) + Rule 5 (tuple `items` → first-element collapse). Module docstring lists all 5 rules.
- `tests/agent/test_moonshot_schema.py` (+178): 10 new cases across `TestRefSiblingStripping` + `TestTupleItems`, plus the one anyOf-collapse expectation update.

## Validation
| | Result |
|---|---|
| `tests/agent/test_moonshot_schema.py` | 42/42 |
| Adjacent moonshot/kimi tests | 98/98 |
| E2E (mixed schema combining all 5 rules) | All fire together; `$defs` target descriptions preserved; `minItems`/`maxItems` survive tuple collapse |

## Source
anomalyco/. Originally scouted in #18130.