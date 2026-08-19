**fix(kanban): honor severity thresholds in diagnostics**

Salvages #26431 by @LeonSGP43.

Dashboard `list_diagnostics` endpoint used exact-match equality so `--severity warning` hid `error` and `critical`. Adds `severity_at_or_above()` helper to `kanban_diagnostics` (centralizing the threshold semantics) and uses it in the dashboard endpoint. The CLI was already using `SEVERITY_ORDER.index` comparison correctly so no CLI behavioral change.

Original branch was stale; applied substantive change manually onto current main. Authorship preserved via rebase merge.

## Validation
- New test test_severity_at_or_above_uses_threshold_semantics passes.