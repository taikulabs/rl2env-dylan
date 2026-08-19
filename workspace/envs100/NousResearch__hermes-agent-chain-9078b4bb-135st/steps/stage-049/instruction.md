**fix(container): detect dashboard role under s6-overlay v3**

Salvages #49238 by @kyssta-exe, and completes the fix.

## Summary

When the gateway and dashboard run as **separate containers sharing a bind-mounted `HERMES_HOME`**, the dashboard container starts its own `gateway-default` in addition to the gateway container's. Both then long-poll `getUpdates` on the same Telegram bot token, producing continuous `409 Conflict: terminated by other getUpdates request` and unreliable delivery — which surfaces to the user as the agent "forgetting" the conversation mid-flow (issue #49196).

`container_boot.main()` is already written to skip per-profile gateway reconciliation in a dashboard container, but the role detector never fired under **s6-overlay v3**.

## Why this matters

Confirmed reproducing on current `main` (s6-overlay **v3.2.3.0**). PID 1 is `s6-svscan`, and the real container command lives on the rc.init-launched process:

```
/bin/sh -e /run/s6/basedir/scripts/rc.init top \
    /opt/hermes/docker/main-wrapper.sh dashboard --host 0.0.0.0 --port 9119 --no-open --insecure
```

In a two-container repro (gateway + dashboard, shared `HERMES_HOME`, `desired_state: running`), the **dashboard** container's `s6-svstat /run/service/gateway-default` comes back `up` and `container-boot.log` logs `profile=default action=started` — the dual-gateway contention the issue describes.

## Why this is a salvage + completion, not just a merge

@kyssta-exe's #49238 correctly fixed **`_read_container_argv()`** to locate the rc.init-launched `main-wrapper.sh` process under s6-overlay v3 (commit cherry-picked here with authorship preserved). But the skip still never fired: the role flows through **`_strip_container_argv_prefix()`**, which only peeled a prefix when `args[0]` was `init` / `main-wrapper.sh` / `hermes`. Under v3 the matched argv begins with `/bin/sh`, so nothing was stripped, `_is_dashboard_container()` stayed `False`, and the dashboard reconciled anyway.

Verified directly against a live container's `/proc` and end-to-end across three image builds: with **only** #49238 applied, the dashboard container still starts `gateway-default` — behavior identical to unfixed `main`. The strip-prefix change is the load-bearing half that was missing.

## Diff

- `hermes_cli/container_boot.py`
  - `_read_container_argv()` (from #49238): try PID 1 first, then scan `/proc/*/cmdline` for the process whose argv contains `main-wrapper.sh` (the rc.init-launched PID under s6 v3).
  - `_strip_container_argv_prefix()`: drop everything up to and including the `main-wrapper.sh` token — the stable boundary the image owns — instead of matching launcher tokens positionally. One rule now covers both the v2 (`/init …`) and v3 (`/bin/sh -e …rc.init top …`) shapes, and it also repairs `_is_legacy_gateway_run_request()` under v3 (it shares the same helper — the issue called this out).
- `tests/hermes_cli/test_container_boot.py`
  - Extend the dashboard true/false parametrize sets with the s6-v3 argv shape.
  - Add `test_main_skips_reconcile_in_dashboard_container_s6v3` exercising `main()` end-to-end with the v3 argv.
  - Add an autouse fixture defaulting `_read_container_argv()` to empty so the suite is hermetic. The new `/proc`-wide scan otherwise picks up *other* hermes containers' `main-wrapper.sh` processes visible in a shared host `/proc`, flaking any test that reconciles without injecting `container_argv`. (Production is unaffected — inside the container `/proc` is the container's own PID namespace.)

## Verification

- `scripts/run_tests.sh tests/hermes_cli/test_container_boot.py tests/hermes_cli/test_service_manager.py` — 113 pass.
- **Mutation:** reverting just the `_strip_container_argv_prefix` change fails exactly the 2 new v3 assertions and leaves the v2 cases green — the new tests genuinely lock the fix.
- **E2E A/B on current `main`** (two containers, shared `HERMES_HOME`, merged-tree image built from this branch):
  - Unfixed `main`: dashboard container → `gateway-default` **up** (bug).
  - This branch: `reconc

…(truncated)