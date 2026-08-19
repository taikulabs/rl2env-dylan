**fix(tui): harden Terminal.app rendering and color paths**

## Summary
- Fixes Terminal.app rendering corruption by disabling fast-echo there and forcing Apple Terminal onto the safer default color path unless `HERMES_TUI_TRUECOLOR=1` is explicitly set.
- Sanitizes incoming ANSI text before `<Ansi>` rendering so only SGR styling is preserved while cursor/screen/title control sequences are stripped.
- Keeps `hermes --tui --dev` reliable by prebuilding `@hermes/ink` exports before launching tsx, with regression tests for all new behavior.