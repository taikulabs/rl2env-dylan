**feat(cli): add dynamic shell completion for bash, zsh, and fish**

## Summary

Salvage of PR #9476 by @leozeli. .

Replaces the hardcoded, stale shell completion stubs in `profiles.py` with a dynamic generator that walks the live argparse parser tree at runtime. Adds fish shell support in both the completion generator and `install.sh`.

### Changes

**From contributor (cherry-picked):**
- New `hermes_cli/completion.py` — dynamic parser walker generates bash/zsh/fish completions from the live argparse tree. No new dependencies.
- `hermes_cli/main.py` — adds missing subcommands to `_SUBCOMMANDS` in `_coalesce_session_name_args()`, wires new completion generator, adds fish as a shell choice
- `scripts/install.sh` — fish shell PATH setup (`fish_add_path`, `~/.config/fish/config.fish`, skips `~/.profile` for fish)
- 17 tests covering parser walking, output generation, syntax validation, drift prevention

**Follow-up fixes (ours):**
- Preserved profile name tab-completion that was lost in the switch from static to dynamic generators:
  - Bash: `_hermes_profiles()` helper + `-p`/`--profile` completion + profile action→name completion
  - Zsh: `_hermes_profiles()` function + `-p`/`--profile` argument spec + profile action case
  - Fish: `__hermes_profiles` function + `-s p -l profile` flag + profile action completions
- Removed dead fallback path in `cmd_completion()` that imported old static generators from `profiles.py`
- 11 additional regression-prevention tests for profile completion

### Usage

```bash
# Bash — add to ~/.bashrc
eval "\$(hermes completion bash)"

# Zsh — add to ~/.zshrc
eval "\$(hermes completion zsh)"

# Fish — add to config
hermes completion fish | source
```