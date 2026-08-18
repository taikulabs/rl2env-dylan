**chore: prepare Hermes for Homebrew packaging**

## Summary

Salvage of PR #4049 by @Yabuku-xD.

Prepares the codebase for Homebrew formula packaging without changing the release versioning scheme or breaking existing installs.

## What changed (and where to look if something breaks)

### 1. `faster-whisper` moved from base deps to `[voice]` extra (pyproject.toml)

**What:** `faster-whisper>=1.0.0,<2` removed from `dependencies`, added to `[voice]` optional extra alongside `sounddevice` and `numpy`.

**Why:** `faster-whisper` pulls in `ctranslate2` and `onnxruntime` which are wheel-only (no source tarballs). Homebrew builds from source, so these break the formula.

**Risk if broken:** Users who installed with plain `pip install hermes-agent` (no extras) would lose local STT transcription. Both import sites are lazy-guarded (`_HAS_FASTER_WHISPER` check in `transcription_tools.py`, function-level import in `discord-voice-doctor.py`), so no startup crash — just "faster-whisper not installed" at transcription time.

**Red flags to look for:** "faster-whisper not installed" errors during voice transcription. Fix: `pip install hermes-agent[voice]` or `pip install faster-whisper`.

**Files:** `pyproject.toml`

### 2. Managed install system generalized (hermes_cli/config.py)

**What:** Extended existing NixOS-only `is_managed()` to support multiple package managers. New `HERMES_MANAGED=homebrew` value. New functions: `get_managed_system()`, `format_managed_message()`, `recommended_update_command()`. Existing `managed_error()` now delegates to `format_managed_message()`.

**Why:** Homebrew installs should not try to `git pull` self-update.

**Risk if broken:** If `get_managed_system()` incorrectly returns non-None for normal installs, `hermes update` and gateway `/update` would be blocked. The env var check is explicit (`HERMES_MANAGED` must be set), and `.managed` marker file check is unchanged.

**Red flags to look for:** "Cannot update: managed by..." message when `HERMES_MANAGED` is NOT set. Banner showing "brew upgrade" instead of "hermes update" on normal installs.

**Files:** `hermes_cli/config.py`, `hermes_cli/main.py` (cmd_update, cmd_version), `hermes_cli/banner.py`, `hermes_cli/plugins_cmd.py`, `gateway/run.py` (_handle_update_command)

### 3. `get_optional_skills_dir()` added (hermes_constants.py)

**What:** New function that checks `HERMES_OPTIONAL_SKILLS` env var, falls back to provided default path, then to `HERMES_HOME/optional-skills`. Used in 4 call sites that previously hardcoded `repo_root / "optional-skills"`.

**Why:** Homebrew installs ship optional-skills to `pkgshare/`, outside the Python package tree.

**Risk if broken:** Optional skill discovery/installation could fail if the function returns a wrong path. Without `HERMES_OPTIONAL_SKILLS` set, it falls back to the exact same path as before (repo-relative `optional-skills/`).

**Red flags to look for:** "skill not found" for official optional skills, `hermes skills install official/...` failures, `/claw` command errors about missing migration script.

**Files:** `hermes_constants.py`, `gateway/run.py` (_check_unavailable_skill), `hermes_cli/claw.py`, `hermes_cli/setup.py`, `tools/skills_hub.py` (OptionalSkillSource)

### 4. Release script improvements (scripts/release.py)

**What:** Builds sdist/wheel artifacts attached to GitHub releases. Better error handling (returns CompletedProcess instead of raising). Graceful `gh` CLI missing handling. Refactored same-day tag logic.

**Why:** Homebrew formulas target semver-named sdist assets, not CalVer tag tarballs.

**Risk if broken:** Only affects `hermes release` workflow, not user installs. If `python -m build` isn't available, gracefully skips artifact building.

**Files:** `scripts/release.py`

### 5. New files (no risk to existing installs)

- `MANIFEST.in` — ensures `skills/` and `optional-skills/` are included in sdists
- `packaging/homebrew/hermes-agent.rb` — template Homebrew formula (placeholder sha256)
- `packaging/homebrew/README.md` — packaging notes

…(truncated)