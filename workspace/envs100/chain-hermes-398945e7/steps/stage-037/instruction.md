**feat(curator): show most-used and least-used skills in `hermes curator status`**

## Summary
`hermes curator status` already surfaces 'least recently used' skills. Add 'most used' and 'least used' rankings by `use_count` so users can see which agent-created skills actually get exercised, not just when they were last touched.

## What changed
`hermes_cli/curator.py` `_cmd_status()` gains two new sections below the existing 'least recently used' block:

- **most used (top 5)** — sorted by `use_count` desc. Hidden when every skill has `use_count=0` (fresh installs have nothing meaningful to show here).
- **least used (top 5)** — sorted by `use_count` asc. Always shown when there's any agent-created skill.

Both include `use=`, `view=`, and `last_used=` columns for a quick read.

## Why now
`use_count` only became a meaningful signal after PR #17932 wired `bump_use()` into the three real skill-activation paths (slash invocation, `--skill` preload, `skill_view` tool call).  this block would have shown all zeros.

## Validation

E2E example (6 skills with varied use counts):

```
most used (top 5):
  top-dog                                   use= 42  view=  0  last_used=0s ago
  runner-up                                 use= 25  view=  0  last_used=0s ago
  middling                                  use= 10  view=  0  last_used=0s ago
  touched-once                              use=  1  view=  0  last_used=0s ago
  never-used-a                              use=  0  view=  0  last_used=never

least used (top 5):
  never-used-a                              use=  0  view=  0  last_used=never
  never-used-b                              use=  0  view=  0  last_used=never
  touched-once                              use=  1  view=  0  last_used=0s ago
  middling                                  use= 10  view=  0  last_used=0s ago
  runner-up                                 use= 25  view=  0  last_used=0s ago
```

Tests: 3 new in `tests/hermes_cli/test_curator_status.py` (happy path, zero-use suppression, no-skills clean empty). `scripts/run_tests.sh tests/hermes_cli/test_curator_status.py tests/agent/test_curator.py` → 41 passed.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_curator_status.py`