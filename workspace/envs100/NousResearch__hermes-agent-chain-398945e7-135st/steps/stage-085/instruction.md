**fix(skills): rescan skill_commands cache when platform scope changes (salvage #14570)**

## Summary

Salvages #14570 by @LeonSGP43 — credited via `Co-authored-by`.

.

## The bug

`agent/skill_commands.py` kept a process-global `_skill_commands` dict that was seeded by whichever platform scanned first. `get_skill_commands()` only rescanned when the cache was empty, so a long-lived gateway serving Telegram + Discord + Slack silently returned the first platform's `skills.platform_disabled` view to all subsequent callers.

Repro on main:

```python
os.environ['HERMES_PLATFORM'] = 'telegram'
scan_skill_commands()                 # -> telegram view (alpha disabled)
os.environ['HERMES_PLATFORM'] = 'discord'
get_skill_commands()                  # -> still telegram view (BUG)
```

## The fix

- Track the platform scope the cache was populated for (`_skill_commands_platform`).
- `get_skill_commands()` now rescans when the currently-active platform differs from that scope.
- Platform resolution uses the same precedence as `tools.skills_tool._is_skill_disabled`: `HERMES_PLATFORM` env var, then `HERMES_SESSION_PLATFORM` from the gateway session context, else `None`.
- `None` (classic CLI, RL rollouts, standalone scripts) is a valid cache key, so those paths keep a single cached scan.

## Alternatives considered

Two other open PRs attempted this fix:

- #14594 (draix) calls `_get_disabled_skill_names(resolved_platform)` but that function takes no argument. The `TypeError` is swallowed by the outer `except Exception`, so the scan silently returns empty for every platform. Verified by applying the patch and running the repro — both `telegram` and `discord` return `[]`.
- #15375 (Tranquil-Flow) caches per-platform copies of the same global scan result. Because the disabled-skill filter is applied inside `scan_skill_commands()` (not at read time), every per-platform view is still the first-platform view. Verified: both telegram and discord return `['/beta']`.

## Tests

- New regression test `test_get_skill_commands_rescans_when_platform_scope_changes` covers telegram → discord → telegram transitions inside a single process.
- Full `tests/agent/test_skill_commands.py` passes (36/36, hermetic run via `scripts/run_tests.sh`).