**fix: add missing mattermost/matrix/dingtalk toolsets + platform consistency tests (salvage #3512)**

## Summary

Mattermost users crash with `KeyError` on every message because `"mattermost"` was missing from `tools_config.py` PLATFORMS. Matrix and dingtalk had PLATFORMS entries but no toolset definitions in `toolsets.py`, and all three were missing from `skills_config.py`.

Cherry-picked from PR #3512 by @MPavleski (authorship preserved).

### Follow-up additions:
- Added `homeassistant` to `skills_config.py` PLATFORMS (was in tools_config but missing from skills_config)
- Added 3 consistency tests that cross-check all platforms have matching toolset definitions, gateway includes, and skills_config entries — prevents this class of bug from recurring