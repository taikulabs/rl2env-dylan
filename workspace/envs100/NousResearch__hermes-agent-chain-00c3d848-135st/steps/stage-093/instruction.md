**feat(security): make secret redaction off by default**

## Summary
Secret redaction (`security.redact_secrets`) now defaults to `false`. New installs get pass-through tool output; users who want the masking behavior opt in with `hermes config set security.redact_secrets true`.

Existing users who already have `redact_secrets: true` in their config.yaml keep redaction on — the config-YAML → env-var bridges in `hermes_cli/main.py` and `gateway/run.py` are unchanged and still respect explicit settings.

## Changes
- `hermes_cli/config.py`: `DEFAULT_CONFIG[security][redact_secrets]` True → False; updated `_SECURITY_COMMENT` and `_COMMENTED_SECTIONS` to reflect new default.
- `agent/redact.py`: env-var fallback flipped — requires explicit opt-in (`1`/`true`/`yes`/`on`) instead of implicit-on-unless-disabled.
- `website/docs/user-guide/configuration.md`: documented new default and opt-in guidance.
- `skills/autonomous-ai-agents/hermes-agent/SKILL.md`: flipped user guidance — default is off, enable with `security.redact_secrets true`.
- `tests/hermes_cli/test_redact_config_bridge.py`: renamed `test_redact_secrets_default_true_when_unset` → `_default_false_`, added `test_redact_secrets_true_in_config_yaml_is_honored` for the opposite direction.

## Validation
| Scenario | Env var | config.yaml | Expected `_REDACT_ENABLED` |
|---|---|---|---|
| Brand new install | unset | no `security` key | False |
| Opt-in via config | unset | `redact_secrets: true` | True |
| Opt-in via .env | `true` | anything | True |
| Opt-out via config | unset | `redact_secrets: false` | False |
| .env beats config | `true` | `redact_secrets: false` | True |

All 79 targeted tests pass (`scripts/run_tests.sh tests/hermes_cli/test_redact_config_bridge.py tests/agent/test_redact.py`).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_redact_config_bridge.py`