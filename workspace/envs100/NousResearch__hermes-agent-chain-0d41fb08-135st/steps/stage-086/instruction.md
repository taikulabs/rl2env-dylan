**fix(nix): gate matrix extra to Linux in [all] profile**

## Summary

 — Matrix does not work on NixOS setup.

### Problem
The `[matrix]` extra was completely excluded from the `[all]` install profile because `python-olm` (a dependency of `matrix-nio[e2e]`) is upstream-broken on modern macOS (archived libolm, C++ errors with Clang 21+). This meant NixOS users — who typically install via `[all]` — got no Matrix support at all, even though `python-olm` builds fine on Linux.

### Fix
Add a `sys_platform == 'linux'` environment marker to the `[all]` profile entry:
```toml
"hermes-agent[matrix]; sys_platform == 'linux'",
```

This pulls in Matrix support on Linux (including NixOS) while continuing to skip the broken macOS build. Users on macOS who need Matrix can still install manually via `pip install 'hermes-agent[matrix]'`.

### Test changes
Updated `test_matrix_extra_linux_only_in_all()` to verify:
- `hermes-agent[matrix]` is **not** unconditionally in `[all]` (would break macOS)
- A Linux-gated variant **is** present in `[all]`

### Notes
- The existing `[matrix]` extra definition is untouched — the marker only affects the `[all]` aggregate.
- This is the short-term fix mentioned in the issue. The long-term fix (replacing `matrix-nio` with `mautrix`) is tracked separately.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_project_metadata.py`