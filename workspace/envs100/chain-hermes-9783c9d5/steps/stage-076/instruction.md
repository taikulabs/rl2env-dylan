**fix(skills): stop marking persisted env vars missing on remote backends**

Salvage of PR #3452 (kentimsit).

Removes the remote-backend short-circuit in `skill_view()` and `_remaining_required_environment_names()` that marked ALL required env vars as missing on Docker/SSH/Modal/Daytona/Singularity backends — even when the vars were already persisted in `~/.hermes/.env`.

Skills now correctly show `setup_needed=false` when vars are available, regardless of backend.

81 skill tests pass.

**Note:** This fixes the readiness check only. The actual forwarding of env vars into remote containers is a separate mechanism (`docker_forward_env` config) that doesn't yet auto-populate from the skill passthrough registry — tracked as a future enhancement.

. .

Co-Authored-By: kentimsit <kentimsit@users.noreply.github.com>

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_skill_env_passthrough.py`
- `tests/tools/test_skills_tool.py`