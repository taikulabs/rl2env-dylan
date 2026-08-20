**fix(update): don't count across shallow-clone boundary (bogus '12492 commits behind')**

## Summary
Shallow installer clones no longer report a bogus "12492 commits behind" — the update check now compares tip SHAs across the shallow boundary instead of counting.

**Root cause:** Since installs switched to `git clone --depth 1`, both the startup banner and `hermes update --check` did a plain `git fetch` (silently unshallowing the repo) and then `git rev-list --count HEAD..origin/main`. Counting across the shallow boundary yields a huge nonsense number. The desktop Electron path was fixed in `2950c6fa2`; the Python CLI paths were missed.

## Changes
- `hermes_cli/banner.py` `_check_via_local_git`: detect shallow via `rev-parse --is-shallow-repository`, fetch with `--depth 1` to preserve the boundary, and return `UPDATE_AVAILABLE_NO_COUNT` (renders "⚠ update available") when behind instead of the bogus count.
- `hermes_cli/main.py` `_cmd_update_check`: same shallow guard — fetch `--depth 1` and report presence-only on shallow clones.
- Full (non-shallow) clones keep the exact `rev-list --count` path unchanged.
- Tests: shallow-behind reports no-count and never runs `rev-list --count`; shallow-up-to-date reports 0; full-clone keeps exact count.

## Validation
| Case | Before | After |
|---|---|---|
| Shallow clone, behind | "12492 commits behind" | "⚠ update available" |
| Shallow clone, up to date | (unshallows repo) | up to date, stays shallow |
| Full clone, N behind | N | N (unchanged) |

E2E tested against real shallow clones (`--branch main`, advanced origin): behind → `-1`, up-to-date → `0`, full clone → exact count; repo stays shallow after the check. Unit tests: `tests/hermes_cli/test_update_check.py` (15) + `test_cmd_update.py` (25) + `test_banner_git_state.py` (7) all green.

## Infographic

![shallow-clone update count fix](https://v3b.fal.media/files/b/0a9f503c/W_lugEdsT4weH9rx6HbwD_aGeTOead.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_check.py`