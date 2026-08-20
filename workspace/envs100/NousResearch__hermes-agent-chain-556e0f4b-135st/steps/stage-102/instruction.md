**fix: skills-sh install fails for deeply nested repo structures**

## Summary

A user (Samuraixheart) reported that `hermes skills install skills-sh/davila7/claude-code-templates/senior-backend` fails with:

```
ClawHub fetch for senior-backend resolved version 2.1.1 but could not retrieve file content
Error: Could not fetch 'skills-sh/davila7/claude-code-templates/senior-backend' from any source.
```

**Root cause:** The skill lives at `cli-tool/components/skills/development/senior-backend/` — 4 levels deep in the repo. Our candidate path generation only checks:
- `repo/skill-name/`
- `repo/skills/skill-name/`
- `repo/.agents/skills/skill-name/`
- `repo/.claude/skills/skill-name/`

And the shallow root-dir discovery scan only goes 1 level deep. So deeply nested skills are never found.

## Fix

Added `GitHubSource._find_skill_in_repo_tree()` which uses the **GitHub Trees API** (`/git/trees/{branch}?recursive=1`) to search the entire repo tree in a **single API call**. This efficiently finds SKILL.md files at any depth.

It's wired in as a final fallback in `SkillsShSource._discover_identifier()`, so it only fires when all other (cheaper) methods have failed.

**Verified working** — tested against the actual repo:
```
Found: davila7/claude-code-templates/cli-tool/components/skills/development/senior-backend
Bundle: name=senior-backend, files=[SKILL.md, references/*, scripts/*]
```

## Tests

- 4 new unit tests for `_find_skill_in_repo_tree` (nested, root-level, not-found, API failure)
- 1 new integration test for full fetch-with-tree-fallback flow
- All 91 skills hub tests pass
- Full suite: 6144 passed (2 pre-existing streaming failures unrelated)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_skills_hub.py`