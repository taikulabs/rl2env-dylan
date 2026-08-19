**fix(skills): load symlinked skill slash commands**

## Summary
- Preserve lexical paths under trusted skill roots when loading skill slash commands
- Fix `/skill-name` invocations for skills symlinked under `~/.hermes/skills`
- Add regression coverage for symlinked skill directories

## Why
Skill slash commands cache the discovered skill directory. When that directory is a symlink, `_load_skill_payload()` resolved it before normalizing it for `skill_view()`. If the symlink target lives outside `~/.hermes/skills`, the loader passed an absolute path through and `skill_view()` rejected it with `Non-relative patterns are unsupported`.

This keeps the trusted, visible path under the configured skills root intact before falling back to resolved-path handling.

## Safety
- Only changes path normalization for skill slash/preload loading
- Does not make arbitrary external paths trusted
- Existing `skill_view()` platform, disabled-skill, collision, and warning behavior remains in place