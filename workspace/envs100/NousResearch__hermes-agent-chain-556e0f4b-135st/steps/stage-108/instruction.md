**refactor: remove mini-swe-agent dependency — inline Docker/Modal backends**

## Summary

Drops the mini-swe-agent git submodule entirely. All terminal backends now use hermes-agent's own environment implementations directly — no external dependency needed.

**Motivation:** The litellm supply chain compromise (PR #2796) exposed that mini-swe-agent was pulling in unnecessary transitive deps. Auditing what we actually used from it revealed we'd already outgrown the wrapper — our DockerEnvironment and ModalEnvironment handled 90%+ of the logic themselves, only calling minisweagent for trivial container startup boilerplate.

## What changed

### Docker backend
- Inlined the `docker run -d` container startup (~15 lines of subprocess code)
- Our wrapper already handled execute(), cleanup(), security hardening, volumes, and resource limits
- No behavioral change

### Modal backend
- Import swe-rex's `ModalDeployment` directly instead of going through minisweagent's 90-line passthrough
- Baked the `_AsyncWorker` pattern into `ModalEnvironment` for Atropos async-safety (no more monkey-patching)
- No behavioral change

### Cleanup
- Removed `minisweagent_path.py` (submodule path resolution helper)
- Removed submodule init/install from `install.sh` and `setup-hermes.sh`
- Removed mini-swe-agent from `.gitmodules`
- `environments/patches.py` is now a no-op (kept for backward compat)
- `terminal_tool.py` no longer does sys.path hacking
- `mini_swe_runner.py` guards imports (optional, for RL training only)
- Updated all affected tests
- Updated README.md, CONTRIBUTING.md

## What's NOT affected

All terminal backends behave identically:
- ✓ Local (default — never needed minisweagent)
- ✓ Docker (now uses direct `docker run -d`)
- ✓ Modal (now imports swe-rex directly)
- ✓ SSH, Singularity, Daytona (never needed minisweagent)

## Stats

- 22 files changed, 284 insertions, 592 deletions (net -308 lines)
- 6093 tests pass, 0 failures