**fix(cli): fix doctor checks for Kimi China credentials**

## Summary

Salvage of PR #9720 by @sjz-ks (

Fixes two `hermes doctor` false-negative bugs for `kimi-coding-cn` / Moonshot China credentials:

1. **Missing env hint**: `KIMI_CN_API_KEY` was not in `_PROVIDER_ENV_HINTS`, so `_has_provider_env_config()` returned `False` for China-only Kimi setups — doctor tells users to run `hermes setup` even though their key is configured.

2. **Null-safety crash**: The Kimi China entry in `_apikey_providers` has `base_env=None` (correct — no user-configurable base URL override for the China endpoint), but `os.getenv(_base_env, "")` crashes with `TypeError: str expected, not NoneType`.

## Changes (2 lines of production code)

- Add `"KIMI_CN_API_KEY"` to `_PROVIDER_ENV_HINTS`
- Guard: `os.getenv(_base_env, "") if _base_env else ""`
- 2 regression tests added