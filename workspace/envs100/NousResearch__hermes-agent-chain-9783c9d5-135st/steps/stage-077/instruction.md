**feat(mattermost): configurable mention behavior — respond without @mention**

## Summary

Adds configurable mention gating for Mattermost channels, matching Discord's existing pattern. Requested by community member neeldhara.

## New Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MATTERMOST_REQUIRE_MENTION` | `true` | Set to `false` to respond to all channel messages without `@mention` |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | _(none)_ | Comma-separated channel IDs where bot responds without `@mention` |

DMs always work regardless of these settings.

## Usage

```bash
# Respond to all messages in all channels
MATTERMOST_REQUIRE_MENTION=false

# Or: respond without mention only in specific channels
MATTERMOST_FREE_RESPONSE_CHANNELS=channel_id_1,channel_id_2
```

## Also fixes

`@mention` is now stripped from the message text before the agent sees it (previously the raw `@botname` was included in the prompt).

## Files Changed

| File | Change |
|------|--------|
| `gateway/platforms/mattermost.py` | Mention gating logic + mention stripping |
| `hermes_cli/config.py` | Env var metadata for setup/doctor |
| `tests/gateway/test_mattermost.py` | 7 new tests + 1 updated test |
| `website/docs/user-guide/messaging/mattermost.md` | Mention Behavior section + env var examples |
| `website/docs/reference/environment-variables.md` | New vars in reference table |

## Tests

46 Mattermost tests pass (7 new).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_mattermost.py`