**feat(plugins): add pre_approval_request / post_approval_response hooks**

## Summary

Plugins can now observe dangerous-command approval events in real time, on both the CLI-interactive path and the async gateway path. This is the missing hook surface external tools (macOS allow/deny notifiers, Slack alerts, audit logs) need to build approval UX without forking Hermes or running a parallel gateway adapter.

Context: a community request — someone wants to ship a macOS menu-bar app that pops an allow/deny notification whenever Hermes needs approval. Today the only programmatic way is to register a full gateway platform adapter or hook into the TUI JSON-RPC bridge. This PR gives them a one-line plugin registration.

## Changes

- `hermes_cli/plugins.py`: add `pre_approval_request` + `post_approval_response` to `VALID_HOOKS`
- `tools/approval.py`: fire both hooks from `check_all_command_guards` — CLI surface (around `prompt_dangerous_approval`) and gateway surface (around `notify_cb` + blocking `event.wait` loop). Single-chokepoint design — `check_all_command_guards` is the only real user-facing approval path on current main
- `website/docs/user-guide/features/hooks.md`: document both hooks with macOS-notification example
- `tests/tools/test_approval_plugin_hooks.py`: 5 tests (CLI once, CLI deny, plugin-crash resilience, gateway approve, gateway timeout)

## Design

- **Observer-only.** Return values ignored — plugins cannot veto or pre-answer. Use `pre_tool_call` to block a tool before it reaches approval.
- **Crash-safe.** A crashing plugin cannot break the approval flow — `invoke_hook` already swallows per-callback errors, and the local wrapper adds a second layer that logs and swallows dispatch-layer errors too. Verified by `test_plugin_hook_crash_does_not_break_approval`.
- **Lazy-imported.** Approval module is imported very early, long before plugins are discovered — the helper lazy-imports `hermes_cli.plugins.invoke_hook` and no-ops if the plugin system isn't available.
- **Both surfaces fire.** `surface="cli"` for interactive CLI/TUI/ACP prompts, `surface="gateway"` for Telegram/Discord/Slack/Matrix/WhatsApp/BlueBubbles/etc.
- **Timeout reported explicitly.** `post_approval_response` gets `choice="timeout"` when the gateway prompt expires without a user response, distinct from `"deny"`.

## Validation

```
tests/tools/test_approval_plugin_hooks.py  5 passed
tests/tools/test_approval.py               full existing suite
tests/gateway/test_approve_deny_commands.py full existing suite
tests/hermes_cli/test_plugins.py           full existing suite
tests/hermes_cli/test_hooks_cli.py         full existing suite
──────────────────────────────────────────────────────
total                                      224 passed
```

## Example usage (documented in hooks.md)

```python
import subprocess

def notify_approval(command, description, session_key, **kwargs):
    subprocess.Popen([
        "osascript", "-e",
        f'display notification "{description}: {command[:80]}" with title "Hermes needs approval"',
    ])

def register(ctx):
    ctx.register_hook("pre_approval_request", notify_approval)
```