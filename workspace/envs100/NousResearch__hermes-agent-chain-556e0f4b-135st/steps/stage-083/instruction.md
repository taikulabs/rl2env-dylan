**fix(skills_guard): agent-created dangerous skills ask instead of block**

Salvage of PR #2271 by @redhelix — skills_guard change only (Mission Control adapter excluded as unrelated).

Agent-created skills with critical security findings were silently blocked. Now they're allowed with a warning logged, since the agent created the skill and blocking it entirely is too aggressive.

| Trust Level | Verdict | Before | After |
|------------|---------|--------|-------|
| agent-created | dangerous | Blocked | Allowed (warning logged) |
| agent-created | dangerous + force | Allowed | Allowed |

- Policy table: `block` → `ask` for agent-created dangerous
- `should_allow_install()` returns `None` for ask (tri-state: True/None/False)
- `format_scan_report()` shows `NEEDS CONFIRMATION` for ask
- `skill_manager_tool.py` caller handles `None` — allows with warning

3 files, +26/-8. 53 skills_guard tests pass.