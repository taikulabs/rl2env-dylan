**fix(s6): dot-prefix gateway staging dir so svscan ignores it mid-build (arm64 EACCES flake)**

## Infographic

![s6 dotfile staging](https://v3b.fal.media/files/b/0aa03ac6/-wJcpkl0wj8ZkrQ4y4EpD_qVS6unSv.png)

## Summary

Fixes the arm64-only CI flake on `test_s6_unregister_removes_service_dir_in_live_container`:

```
PermissionError: /run/service/gateway-phase3test.tmp/supervise/event
```

The root cause is a TOCTOU between the profile-gateway **register** staging dir and a concurrent `s6-svscanctl -a` rescan — not, as the test name suggests, anything in the unregister/teardown path.

## Root cause

`register_profile_gateway` (and the boot-reconciler twin `container_boot._register_service`) build each slot in a sibling staging dir **inside `/run/service`** — the scandir `s6-svscan` watches — then atomically rename it to the live `gateway-<profile>` name. The staging dir was named `gateway-<profile>.tmp`: a **non-dotfile**.

`s6-svscan` skips any scandir entry whose name begins with `.`, but a non-dotted name is fair game. So when a rescan fires while the staging dir is half-built — the cont-init reconciler registering `gateway-default`, or a sibling register, both call `s6-svscanctl -a` — `s6-svscan` sees a dir with a valid `type`/`run` and **supervises it**: `s6-supervise gateway-<p>.tmp` spawns **as root** and `mkdir`s `supervise/` root-owned `0700`. The in-flight `_seed_supervise_skeleton` then early-returns on the now-existing `supervise/` and the next `mkdir supervise/event` hits `EACCES`.

It's **arm64-only** because the native-arm runner's wider scheduling jitter lets the rescan land inside the ~millisecond seed window; amd64 ran the register/unregister cycle 30/30 clean.

Two earlier hypotheses were disproven before landing on this:
- **Cross-test container reuse** — no: `tests/docker/conftest.py`'s `container_name` fixture is function-scoped (fresh `docker run` per test) and CI runs per-file isolation.
- **s6-svscan auto-rescans on its own** — no: it runs `-d4` with no `-t`; a half-built staging dir sits unsupervised until an explicit `s6-svscanctl -a`.

## Fix

Dot-prefix the staging dir (`.gateway-<profile>.tmp`) in **both** register paths so `s6-svscan` can never supervise it mid-build. The atomic rename to the dotless live name is unchanged, so the published slot is identical.

- `hermes_cli/service_manager.py` — `S6ServiceManager.register_profile_gateway`
- `hermes_cli/container_boot.py` — `_register_service`

This is the true fix. Making `_seed_supervise_skeleton`'s `mkdir`/`chmod` EACCES-tolerant would only paper over a root-owned `supervise/` — the slot would then be unusable by the unprivileged `hermes` user anyway.

## Verification

Proven end-to-end on a real s6 image (amd64), forcing the rescan rather than relying on the timing window:

| Staging dir name | `s6-svscanctl -a` rescan result |
|---|---|
| `gateway-raceprobe.tmp` (old, non-dotted) | **SUPERVISED owner=root** — the bug |
| `.gateway-raceprobe.tmp` (fix, dotted) | **NOT-SUPERVISED** — skipped by s6-svscan |

Tests:
- `tests/docker/test_s6_profile_gateway_integration.py::test_s6_dotfile_staging_dir_is_ignored_by_svscan_rescan` — new docker-harness regression that asserts **both** the control (non-dotted IS supervised) and the fix (dotted is NOT), against real s6. Arch-independent: it forces the rescan, so it guards the fix on the amd64 job too.
- `tests/hermes_cli/test_service_manager.py::test_s6_register_staging_dir_is_dotfile_hidden_from_svscan` — unit test asserting the staging dir handed to `_seed_supervise_skeleton` is dot-prefixed.
- Updated `tests/hermes_cli/test_container_boot.py` stale-`.tmp`-cleanup test + the no-remnants glob for the new dot-prefixed name.

```
tests/hermes_cli/test_service_manager.py + test_container_boot.py: 117 passed
tests/docker/test_s6_profile_gateway_integration.py: 3 passed (real s6 image, amd64)
```