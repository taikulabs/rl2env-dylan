**feat(skills): add garrytan/gstack as default Skills Hub tap**

## Summary

Add the [gstack](https://github.com/garrytan/gstack) community skills repo to the default Skills Hub tap list. Also fixes skill identifier construction for repos with an empty `path` prefix — previously produced `repo//dir_name` with a double slash.

Salvaged from #3386 by @tugrulguner with authorship preserved.

## Changes
- `tools/skills_hub.py`: add gstack tap + fix empty-path identifier construction

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_gateway_restart.py`