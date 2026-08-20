**feat(cron): warn when gateway not running on cron create/list**

## Summary
`hermes cron create` now warns when the gateway isn't running, so users learn up front that their job won't fire.

The cron ticker runs **only inside the gateway** (`_start_cron_ticker`) — there is no standalone cron daemon. With no gateway running, `next_run_at` passes but jobs never fire and `last_run_at` stays null. Manual `hermes cron run` bypasses the ticker and appears to work, masking the cause. This is the most common cron "jobs never fired" report.

`cron list` already showed this warning; `cron create` (the moment the user is most likely to hit it) did not.

## Changes
- `hermes_cli/cron.py`: extract the warning into `_warn_if_gateway_not_running()`; call it from `cron_create` and `cron_list` (dedup); add a `hermes cron status` pointer. Silent when a gateway is running — the gateway `/cron` path is unaffected.
- `tests/hermes_cli/test_cron.py`: regression guards — create/list warn when gateway absent, silent when present.

## Validation
| | Gateway down | Gateway up |
|---|---|---|
| `cron create` | warns | silent |
| `cron list` | warns | silent |

Verified live: real `find_gateway_pids()` returned a running PID → no false nag; forced-absent → warning renders. Targeted suite 7/7 green via `scripts/run_tests.sh`.

## Note on #51038
The reported scheduler defect (polling too slow / no catch-up) does not exist: the ticker polls every 60s and daily jobs already get a 2h catch-up grace window (verified E2E — a daily job 13–23 min late fires; >2h fast-forwards). The real cause was a gateway that was never started. This PR closes the UX gap that led to the report.

## Infographic
![Cron warn when gateway is down](https://v3b.fal.media/files/b/0a9f8abf/BSs6Fg4PYyrbGKdQ-hDzV_Z8vzeBMb.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_cron.py`