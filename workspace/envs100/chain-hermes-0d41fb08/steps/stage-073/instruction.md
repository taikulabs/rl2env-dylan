**security: path traversal fix, Claude Code credential gate, DANGEROUS_PATTERNS gaps**

## Summary
Three security fixes salvaged from PRs #7065, #7009, and #6961. All contributor authorship preserved.

### 1. Skill manager path traversal (PR #7065, @Dusk1e)
Symlinks inside skill directories could escape to arbitrary files for write/patch/remove. Adds `_resolve_skill_target()` with resolved-path containment check. 3 tests.

### 2. Claude Code credential gate (PR #7009, @wanpengxie)
When a user's primary provider fails, the auxiliary fallback chain silently discovered and used Claude Code OAuth tokens from `~/.claude/.credentials.json` without consent. Adds `is_provider_explicitly_configured()` gate — credentials are only used when the user explicitly configured Anthropic. Defense in depth: gate in credential pool + gate in aux client + suppression on `hermes auth remove`. 9 tests.

### 3. DANGEROUS_PATTERNS gaps (PR #6961, @win4r)
Closes 4 bypass categories: heredoc script execution (`python3 <<`), pgrep kill expansion, git destructive ops (reset --hard, push --force, clean -f, branch -D), and chmod+exec combo. 11 new patterns, 23 tests.

## E2E verification
All three fixes verified with real file I/O, real symlink creation, real env var manipulation:
- Symlink escapes blocked for write/patch/remove; legitimate writes pass
- CLAUDE_CODE_OAUTH_TOKEN excluded from explicit config detection; ANTHROPIC_API_KEY included
- All 8 dangerous commands flagged, all 7 safe commands pass (zero false positives)

## Test results
301 targeted tests passing across all affected files.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_approval.py`