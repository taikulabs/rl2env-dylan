**fix(tui): hide reasoning panels immediately**

## Summary
- Make `/reasoning hide` persist `display.sections.thinking: hidden` so existing thinking panels are hidden.
- Apply the matching TUI state update immediately after the slash command succeeds.
- Avoid keeping the progress area visible solely because hidden reasoning text exists.