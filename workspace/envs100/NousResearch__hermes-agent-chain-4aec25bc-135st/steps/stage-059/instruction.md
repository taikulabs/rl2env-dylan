**fix(tirith): suppress .app lookalike_tld false positives in warn verdicts**

Salvage of #24569 by @wesleysimplicio. . Duplicate PR #24562 by @luyao618 (submitted ~8 min earlier) — both contributors credited; closing #24562 with attribution.

## Summary
`.app` is a legitimate ICANN gTLD; Tirith's `lookalike_tld` rule flagging it as suspicious produced noisy approval prompts on normal commands like `curl https://example.app`. `check_command_security()` now downgrades `warn` → `allow` when every finding is `lookalike_tld` for `.app`.

## Invariants preserved
- `block` verdicts never downgraded (including `.app` findings).
- Mixed findings (`.app` + anything else) keep `warn`.
- Other `lookalike_tld` TLDs (`.zip`, etc.) still warn.

## Changes
- `tools/tirith_security.py`: `_is_app_tld_finding()` helper + post-parse downgrade in `check_command_security()`. Scans `value`/`tld`/`detail`/`description`/`message` fields, case-insensitive.
- `tests/tools/test_tirith_security.py`: 15 new tests (`TestAppTldSuppression` + `TestIsAppTldFinding`).

## Validation
| | Result |
|---|---|
| Targeted tests | 90/90 pass (75 existing + 15 new) |
| E2E (real `check_command_security`) | 5/5 scenarios: `.app`-only → allow; `.app`+pipe-to-sh → warn; `.zip` → warn; `.app`+block → block; helper field/case checks |

Authorship preserved via cherry-pick.