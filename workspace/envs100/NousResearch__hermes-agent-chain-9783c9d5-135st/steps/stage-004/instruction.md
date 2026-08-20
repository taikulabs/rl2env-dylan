**fix: stop recursive AGENTS.md walk, load top-level only**

Only load AGENTS.md from the working directory root. The recursive os.walk that collected AGENTS.md from every subdirectory was undesired — matches the cwd-only behavior of CLAUDE.md and .cursorrules.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_prompt_builder.py`