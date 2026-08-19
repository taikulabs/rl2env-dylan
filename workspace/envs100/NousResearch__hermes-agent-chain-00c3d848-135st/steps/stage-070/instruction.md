**feat(update): snapshot pairing data before git pull**

`hermes update` now takes a labeled `pre-update` state snapshot before pulling, and the snapshot set includes pairing JSONs.

## Changes
- `hermes_cli/backup.py`: `_QUICK_STATE_FILES` adds `pairing/`, `platforms/pairing/`, and `feishu_comment_pairing.json`; `create_quick_snapshot()` walks directory entries recursively.
- `hermes_cli/main.py`: `_cmd_update_impl` calls `create_quick_snapshot(label='pre-update')` after 'Found N new commits' and before 'Pulling updates'. Failures are swallowed at debug so they never block an update.
- `tests/hermes_cli/test_backup.py`: 3 tests covering pairing-directory snapshot, pairing-data restore, and empty-dir tolerance.

## Root cause note
#15733 claims `hermes update` cloned and wiped `state.db`, but `_cmd_update_impl` only runs `git fetch` + `git pull --ff-only` on `PROJECT_ROOT` and pairing data doesn't live in `state.db` (it's in `~/.hermes/pairing/`, `~/.hermes/platforms/pairing/`, and Feishu-specific JSONs). The reporter's mechanism is incorrect, but losing pairing approvals is painful regardless — this is belt-and-suspenders insurance so the next user with a similar report has a cheap `/snapshot restore` path.

## Validation
| | Before | After |
|---|---|---|
| Quick snapshot captures pairing | no | yes (dirs + Feishu JSON) |
| `hermes update` takes pre-pull snapshot | no | yes (labeled `pre-update`) |
| test_backup.py | 71 pass | 74 pass |
| E2E (real sqlite + pairing JSON round-trip) | — | passes |

.