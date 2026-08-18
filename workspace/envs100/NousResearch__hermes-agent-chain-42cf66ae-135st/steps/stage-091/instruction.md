**fix: use description as pattern_key to prevent approval collisions**

## Summary
- cherry-pick the substantive fix from #1079 so dangerous command approvals use unique human-readable pattern keys instead of regex-derived prefixes that can collide
- preserve backwards compatibility for legacy `command_allowlist` entries and session approvals that still contain the old regex-derived keys
- add regression tests covering both the original `find` collision and the legacy-key compatibility path