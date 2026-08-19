**fix(desktop): tree-kill Windows terminal descendants**

## Summary
- Route Windows foreground terminal cleanup through `taskkill /T /F` so Git Bash descendants are killed with the wrapper.
- Reuse the host process-tree terminator for local background process kills.
- Tree-kill desktop-managed backend processes on Windows during reset, profile backend teardown, and app quit.

.