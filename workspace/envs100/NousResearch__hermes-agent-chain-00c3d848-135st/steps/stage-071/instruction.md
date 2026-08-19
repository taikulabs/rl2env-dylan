**fix(hindsight): preserve setup config on blank input**

## Summary
- Load existing Hindsight config at the start of the setup wizard
- Seed mode/provider prompts from existing values and keep current text values on blank input
- Preserve explicit zero values such as idle_timeout: 0 and existing HINDSIGHT_* tuning keys
- Remove an unused local variable in the touched plugin file so ruff passes