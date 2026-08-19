**fix(cli): restore stacked tool progress scrollback in TUI**

## Summary

The TUI transition (commits 4970705, f83e86d) replaced stacked per-tool history lines with a single live-updating spinner widget. While the spinner provides a nice live timer for the current tool, it removed the scrollback history that users relied on to see what the agent did during a session.

This restores stacked tool progress lines in `all` and `new` modes by printing persistent scrollback lines via `_cprint()` when tools complete, in addition to the existing live spinner display.

**Reported by:** Community user Mr.D on Discord — the stacked history provides transparency into what the agent is doing, which builds trust.

## What changed

`cli.py`:
- On `tool.started`: store function_args in `_pending_tool_info` (FIFO per function name for concurrent tools)
- On `tool.completed`: pop stored args, format via `get_cute_tool_message()`, print as persistent scrollback line
- `new` mode: tracks `_last_scrollback_tool` to skip consecutive same-tool repeats
- State cleared at end of agent run

**Behavior per mode:**
| Mode | Spinner | Scrollback lines |
|------|---------|-----------------|
| off | no | no |
| new | yes (live timer) | yes (skip consecutive same-tool) |
| all | yes (live timer) | yes (every tool) |
| verbose | yes | no (run_agent.py handles verbose directly) |