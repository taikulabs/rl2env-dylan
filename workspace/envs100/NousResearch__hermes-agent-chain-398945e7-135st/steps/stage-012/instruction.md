**fix(tui): honor launch toolsets**

## Summary
- Pass `--toolsets` from `hermes --tui` into the TUI subprocess.
- Prefer the TUI process toolset override when constructing gateway agents.
- Cover launcher propagation and gateway parsing in tests.