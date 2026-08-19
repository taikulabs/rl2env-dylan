**fix(tui): persist global details mode sections**

## Summary
- Make global `/details <mode>` pin every detail section in live TUI state.
- Persist matching `display.sections.*` values so config sync does not restore built-in section defaults.
- Cover frontend slash handling and gateway config persistence.