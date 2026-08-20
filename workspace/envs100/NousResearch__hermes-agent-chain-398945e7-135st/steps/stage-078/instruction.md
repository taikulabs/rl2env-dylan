**fix(gateway): include external_dirs skills in Telegram/Discord slash commands (salvage #8790)**

## Summary

Salvages #8790 by @luyao618 — credited via `Co-authored-by`.

.

## The bug

Skills declared through `skills.external_dirs` were first-class everywhere EXCEPT gateway slash menus:

| Surface | Sees external skills? |
|---|---|
| `hermes skills list` | Yes |
| `get_skill_commands()` | Yes |
| Agent `/skill-name` dispatch | Yes |
| Telegram `getMyCommands` | **No** |
| Discord slash commands | **No** |

Root cause in `hermes_cli/commands.py` inside `_collect_gateway_skill_entries`:

```python
_skills_dir = str(SKILLS_DIR.resolve())
...
if not skill_path.startswith(_skills_dir):
    continue   # silently drops every external skill
```

## The fix

Widen the accepted prefix set to include every directory in `get_external_skills_dirs()` alongside `SKILLS_DIR`. Also:

- Every prefix is slash-terminated so `/my-skills` cannot accidentally admit `/my-skills-extra`.
- Empty `skill_md_path` values are skipped up front so they can't match a degenerate prefix.
- The hub-exclusion prefix gets the same slash-termination treatment for consistency.

## Tests

- New `test_external_dir_skills_included_in_telegram_menu` covers three cases in one test: local skill present, external skill present, prefix-lookalike sibling directory **not** admitted.
- Full `tests/hermes_cli/test_commands.py` passes (131/131 via hermetic `scripts/run_tests.sh`).

## Why the original PR was  was closed by its author on Apr 30, not rejected by a reviewer. The diff still applies cleanly to current main and the fix is correct, so re-opening the change as a fresh PR with the original author's attribution.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_commands.py`