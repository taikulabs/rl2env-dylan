**feat(skills): support external skill directories via config**

## What this PR does

Adds a `skills.external_dirs` config option that lets users point Hermes at additional skill directories outside `~/.hermes/skills/`. Skills in external dirs are discovered alongside local skills — they show up in the system prompt index, `skills_list`, `skill_view`, and `/skill` slash commands.

Requested by community member **primco** who maintains a shared `~/.agents/skills/` directory across multiple AI tools and didn't want skills locked into Hermes.

## Config

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
```

Paths support `~` expansion and `${VAR}` substitution (existing config feature). Non-existent dirs are silently skipped.

## Design decisions

- **Read-only**: External dirs are only scanned for discovery. `skill_manage` (create/edit/delete) always writes to `~/.hermes/skills/`
- **Local precedence**: If the same skill name exists in both local and external dirs, local wins (first match by name)
- **Security**: Configured external dirs are recognized as trusted in the security check (no warning). Only skills from truly unknown paths trigger the warning
- **Snapshot cache**: The disk snapshot covers only the local dir (unchanged). External dirs are scanned directly on cache miss. The in-process LRU cache covers everything

## Files changed (7 files, +446/-93)

| File | Change |
|------|--------|
| `agent/skill_utils.py` | `get_external_skills_dirs()` and `get_all_skills_dirs()` helpers |
| `agent/prompt_builder.py` | Scan external dirs in `build_skills_system_prompt()` |
| `tools/skills_tool.py` | `_find_all_skills()`, `skill_view()`, security check updated |
| `agent/skill_commands.py` | `/skill` slash commands discover external skills |
| `hermes_cli/config.py` | `skills.external_dirs` in DEFAULT_CONFIG |
| `cli-config.yaml.example` | Document the option |
| `tests/agent/test_external_skills.py` | 11 new tests |

## Tests

- 11 new tests covering: config parsing, path validation, dedup, local precedence, skill_view resolution
- 590 existing tests pass (1 pre-existing failure unrelated to this change)