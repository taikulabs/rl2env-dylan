**fix: use description as pattern_key to prevent approval collisions**

## Summary
- 
- preserve backwards compatibility for legacy `command_allowlist` entries and session approvals that still contain the old regex-derived keys
- add regression tests covering both the original `find` collision and the legacy-key compatibility path
