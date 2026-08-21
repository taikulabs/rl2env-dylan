**feat(webhook): dynamic subscriptions via hermes webhook CLI + skill**

## Summary

Adds `hermes webhook` CLI subcommand and a skill for managing dynamic webhook subscriptions — enabling event-driven agent activation from external services (GitHub, Stripe, CI/CD, IoT, monitoring, etc.) without editing config.yaml.

**Zero new model tools. Zero toolset changes.** The agent uses the CLI commands via the terminal tool, guided by the `webhook-subscriptions` skill.

## CLI Commands

All commands require the webhook platform to be enabled. If not configured, they print setup instructions (wizard, manual config, or env vars).

```bash
# Create a subscription — returns webhook URL + HMAC secret
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}" \
  --deliver telegram --deliver-chat-id "-100123456"

# List all dynamic subscriptions
hermes webhook list

# Remove a subscription
hermes webhook remove github-issues

# Send a test POST to verify it works
hermes webhook test github-issues
```

## How It Works

1. `hermes webhook subscribe` writes to `~/.hermes/webhook_subscriptions.json`
2. The webhook adapter hot-reloads this file on each incoming request (mtime-gated, negligible overhead)
3. When a matching POST arrives, the adapter formats the prompt template and triggers an agent run
4. The agent's response is delivered to the configured target (Telegram, Discord, GitHub, etc.)

Static routes from `config.yaml` always take precedence over dynamic ones with the same name. No gateway restart needed.

## Enabled Gate

Every `hermes webhook` subcommand checks `platforms.webhook.enabled` in config first. If webhooks aren't set up, the user sees:

```
Webhook platform is not enabled. To set it up:

  1. Run the gateway setup wizard:
     hermes gateway setup

  2. Or manually add to ~/.hermes/config.yaml:
     ...

  3. Or set environment variables in ~/.hermes/.env:
     ...
```

## Skill

`skills/devops/webhook-subscriptions/SKILL.md` covers:
- Setup prerequisites and three configuration methods
- All CLI commands with full option reference
- Prompt template syntax (`{dot.notation}`)
- Common patterns: GitHub issues/PRs, Stripe payments, CI/CD builds, monitoring alerts
- Security (HMAC, static route precedence)
- Troubleshooting (gateway not running, signature mismatch, firewall, event filtering)

## Files Changed

| File | Change |
|------|--------|
| `hermes_cli/webhook.py` | New — CLI command implementation with enabled gate |
| `hermes_cli/main.py` | Subparser wiring for `hermes webhook` |
| `gateway/platforms/webhook.py` | Dynamic route hot-reload (`_reload_dynamic_routes`) |
| `skills/devops/webhook-subscriptions/SKILL.md` | New — agent skill |
| `website/docs/user-guide/messaging/webhooks.md` | Dynamic Subscriptions section |
| `website/docs/reference/cli-commands.md` | `hermes webhook` reference |
| `tests/hermes_cli/test_webhook_cli.py` | 18 tests — CRUD, persistence, enabled gate |
| `tests/gateway/test_webhook_dynamic_routes.py` | 6 tests — adapter hot-reload |

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_webhook_dynamic_routes.py`
- `tests/hermes_cli/test_webhook_cli.py`