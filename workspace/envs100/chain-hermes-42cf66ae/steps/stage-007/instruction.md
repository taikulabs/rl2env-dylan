**fix(doctor): treat configured honcho as available**

Direct merge of #962 would silently drop #736's Honcho Memory diagnostic section from doctor.py due to staleness (105 commits behind). Cherry-pick preserves both.

## Changes
- Doctor-only config check promotes honcho to available when `HonchoClientConfig.from_global_config()` resolves to enabled + API key present
- Runtime tool gate unchanged
- 7 regression tests

Co-authored-by: PeterFile <PeterFile@users.noreply.github.com>

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_doctor.py`