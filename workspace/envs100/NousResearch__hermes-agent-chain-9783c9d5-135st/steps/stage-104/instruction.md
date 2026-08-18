**feat: mount skills directory into remote backends (Modal, Docker)**

## Summary

Skills with `scripts/`, `templates/`, and `references/` subdirectories need those files available inside sandboxed execution environments. Previously only individual credential files were mounted — the skills directory itself was completely absent from Modal/Docker sandboxes, meaning skill scripts couldn't be executed.

Reported by ilovescience (Tanishq) who uses Modal as a terminal backend — `~/.hermes/skills/` didn't exist at all in the sandbox.

## Changes

| File | Change |
|------|--------|
| `tools/credential_files.py` | Add `get_skills_directory_mount()` — returns `$HERMES_HOME/skills/` mount info |
| `tools/credential_files.py` | Fix `name`/`path` key fallback — skills using `name` in `required_credential_files` were silently skipped |
| `tools/environments/modal.py` | Mount skills dir via `Mount.from_local_dir()` at sandbox creation |
| `tools/environments/docker.py` | Mount skills dir as read-only bind mount |
| `tests/tools/test_credential_files.py` | 8 new tests |

## How it works

The skills tree is mounted **read-only** at `/root/.hermes/skills/` inside the container. This means:
- Skill scripts are executable in the remote env (`python /root/.hermes/skills/.../scripts/setup.py`)
- The agent's context references to skill paths resolve correctly
- No config, .env, auth.json, or other sensitive files leak — only the skills tree

## Tests

- 8 new tests: name/path fallback, skills dir mount presence/absence, custom container base, missing file reporting
- 38 existing docker/modal tests pass
- All tools tests pass