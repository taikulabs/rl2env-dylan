**fix(security): validate domain/service params in ha_call_service to prevent path traversal**

## Summary

Adds `_SERVICE_NAME_RE` format validation for `domain` and `service` parameters in `ha_call_service` before they're interpolated into `/api/services/{domain}/{service}`. Without this, path traversal payloads like `domain="../../api/config"` could reach arbitrary HA endpoints, and payloads like `domain="shell_command/../light"` could bypass the `_BLOCKED_DOMAINS` blocklist.

## Changes
- `tools/homeassistant_tool.py`: Added `_SERVICE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")` and validation before blocklist check
- `tests/tools/test_homeassistant_tool.py`: 11 regression tests covering traversal, bypass, and edge cases

## Test results
All 64 HA tests pass, zero regressions.