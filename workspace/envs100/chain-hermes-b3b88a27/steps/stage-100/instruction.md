**fix(model_switch): enumerate dict-format models in /model picker + section-3 refinements**

Multi-model custom providers now show all their models in the `/model` picker instead of just the default. Salvage of @farion1231's #12505 with section-3 refinements drawn from @YangManBOBO's #11534.

## Changes
- `hermes_cli/model_switch.py` (sections 3 + 4 of `list_authenticated_providers()`):
  - Enumerate dict-format `models:` in both the `providers:` dict path and the `custom_providers:` list path ( and #9148)
  - Section 3: accept canonical `base_url` (matches Hermes's writer), keep `api`/`url` as fallbacks
  - Section 3: accept singular `model` as a `default_model` synonym
  - Section 3: `seen_slugs` dedup guard so a slug appearing in both `providers:` and `custom_providers:` emits one row
- 8 regression tests (6 from #12505 + 2 on top for the new section-3 behavior)
- `scripts/release.py`: AUTHOR_MAP entry for farion1231@gmail.com

## Validation
| | Before | After |
|---|---|---|
| `providers:` dict entry w/ dict-format `models:` | `(0 models)` | enumerates every key |
| `custom_providers:` entry w/ dict-format `models:` | only singular `model:` | enumerates every key, dedupes singular |
| `providers:` entry w/ canonical `base_url`/`model` | empty `api_url`, no default | resolves the same as legacy shape |
| Same slug in both `providers:` and `custom_providers:` | 2 picker rows | 1 row (providers: wins) |

Targeted test run:

```
tests/hermes_cli/test_model_switch_custom_providers.py ....... (9)
tests/hermes_cli/test_user_providers_model_switch.py   ............. (13)
22 passed in 0.78s
```

E2E verified against a real `config.yaml` containing all four shapes (new-style providers dict with dict models, legacy providers dict with list models, custom_providers with dict models + singular default, custom_providers with dict models only). All four rows surface with correct model counts, no duplicate slugs.

## Credit
- @farion1231 (PR #12505) — baseline implementation + tests for sections 3 and 4
- @YangManBOBO (PR #11534) — section-3 base_url/model fallbacks and dedup guard

Supersedes: #12505, #11534, #11546, #11968, #11403, #9864, #10326, #11130 — all solve subsets of the same bug.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_user_providers_model_switch.py`