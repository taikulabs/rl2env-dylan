**fix(gateway): detect legacy hermes.service + mark --replace SIGTERM as planned**

## Summary
Ends the  SIGTERM flap loop between two gateway units (e.g. legacy `hermes.service` + current `hermes-gateway.service`) fighting for the same bot token.

Root cause: Luis ran an older install that wrote `hermes.service` before we renamed to `hermes-gateway.service`. Both units remained enabled. #5646 made SIGTERM exit 1 so real kills get revived by systemd — which also turned `--replace` takeovers into "losses" that systemd revives 30s later, flapping indefinitely.

## Changes
- **`hermes_cli/gateway.py`**: `_find_legacy_hermes_units()` (explicit allowlist of `hermes.service` + ExecStart content check — profile units `hermes-gateway-<profile>.service` are NEVER matched), `has_legacy_hermes_units()`, `print_legacy_unit_warning()`, `remove_legacy_hermes_units()`. `systemd_install` now offers to remove legacy units before installing. Status/setup paths print the legacy warning alongside the existing scope-conflict warning.
- **`hermes_cli/main.py`**: new `hermes gateway migrate-legacy` subcommand (with `--dry-run` and `-y`).
- **`hermes_cli/setup.py`**: main setup wizard prints the legacy warning.
- **`gateway/status.py`**: `write_takeover_marker()` / `consume_takeover_marker_for_self()` / `clear_takeover_marker()` — short-lived marker (60s TTL, PID + start_time scoped) that lets the `--replace` target exit 0 instead of 1.
- **`gateway/run.py`**: `start_gateway(replace=True)` writes the marker before SIGTERM and clears it on success or on permission-denied give-up. `shutdown_signal_handler` consults the marker before setting `_signal_initiated_shutdown`.

## Profile safety (verified in tests)
Legacy detection is an **explicit allowlist** (`_LEGACY_SERVICE_NAMES = ("hermes.service",)`), not a glob. Profile units like `hermes-gateway-coder.service` and `hermes-gateway-orcha.service` are never flagged or touched by any of the new code paths, even when they live in the same search directories.

## Validation
| | Before | After |
|---|---|---|
| Two units installed (`hermes.service` + `hermes-gateway.service`) | 30s flap loop until `StartLimitBurst=5` trips | Install wizard offers to remove the legacy one; explicit `hermes gateway migrate-legacy` available |
| `--replace` takeover SIGTERM | Target exits 1 → systemd revives → collides | Target exits 0 via marker → systemd leaves it stopped |
| Profile unit (`hermes-gateway-coder.service`) | untouched | untouched (explicit allowlist enforces this) |
| Unrelated third-party `hermes.service` | n/a | untouched (ExecStart content check rules it out) |
| Existing status/install paths | n/a | backward compatible (new warnings only appear when legacy exists) |

### Tests added (all passing)
- `TestLegacyHermesUnitDetection` — 10 tests (detection, profile-safety, ExecStart variants, stale-file grace)
- `TestRemoveLegacyHermesUnits` — 8 tests (user + system scope, dry-run, non-root behaviour, profile-safety)
- `TestMigrateLegacyCommand` — 4 tests (subparser registration, dispatch, unsupported platform)
- `TestSystemdInstallOffersLegacyRemoval` — 3 tests (install prompt flow, user decline, skip when no legacy)
- `TestTakeoverMarker` — 11 tests (write, consume-for-self, PID mismatch, start_time mismatch, TTL staleness, malformed, idempotent clear)
- `test_start_gateway_replace_writes_takeover_marker_before_sigterm` — E2E ordering test
- `test_start_gateway_replace_clears_marker_on_permission_denied` — cleanup regression guard

Total: 38 new tests. Full gateway test suite: 3153 passed, 10 pre-existing unrelated failures (signal redaction / telegram approval buttons / whatsapp / internal event bypass — all exist on `main` without these changes).

## Origin story
Discovered while diagnosing a Telegram user's "⚠ Gateway shutting down" loop. `ps aux` showed one live gateway but `systemctl list-units` showed two enabled services, both named "Hermes Gateway" (our current `SERVICE_DESCRIPTION`). Git log confirmed timing: PR #5646 landed 3 days before the user's install version — the flap loop b

…(truncated)