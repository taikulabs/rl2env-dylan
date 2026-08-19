**fix(web): scope dashboard config Reset button to the current tab**

## Summary
Reset in the dashboard Config page now resets only the category you're looking at, not your entire config.yaml.

Reported by @ykmfb001 via X: clicking 'Restore Defaults' (恢复默认值) on the Auxiliary tab wiped the whole config. The button sits next to the category tabs, so users reasonably assumed per-tab scope — it was actually global with no confirmation.

## Changes
- `web/src/pages/ConfigPage.tsx` — `handleReset` scopes to the fields in the current view (active category's fields, or search-matched fields when searching). Only those keys are copied from defaults; the rest of the config is left alone. Added `window.confirm()` naming the scope. Hidden in YAML mode (scoping doesn't map there). Tooltip/aria-label now name the scope, e.g. 'Reset Auxiliary to defaults'.
- `web/src/i18n/{en,zh,types}.ts` — new `resetScopeTooltip` / `confirmResetScope` / `resetScopeToast` strings. `resetDefaults` key preserved for compat.

## Behavior

| View | Before | After |
|---|---|---|
| Category tab → Reset | wipes entire config | resets only that category, with confirm |
| Search → Reset | wipes entire config | resets only matched fields, with confirm |
| YAML mode | wipes entire config | button hidden |
| Reset without Save | form reset, config.yaml untouched | same (clarified in confirm text) |

## Validation
- `tsc -b` clean
- `vite build` clean
- ESLint warnings pre-existing on main (React Compiler memoization hints on unrelated useMemo), unchanged by this PR