**fix(migration): update OpenClaw migration for schema drift**

## Summary

Two-part fix for `hermes claw migrate`:

**1. Schema drift fixes** — OpenClaw restructured internal paths/schemas; our migration was reading stale locations. Consolidates 6 community PRs.

**2. Preview-then-confirm UX** — `hermes claw migrate` now always shows a full dry-run preview before making changes. The user reviews what would be imported, then confirms. Matches the setup wizard flow.

**Salvaged from:** #7869 (SHL0MS), #7860 (SHL0MS), #7861 (SHL0MS), #7862 (SHL0MS), #7864 (SHL0MS), #7868 (SHL0MS)
**Tracking issue:** #7847

## Changes

### Schema drift fixes (`openclaw_to_hermes.py`, +113/-31)

| Fix | What changed |
|-----|-------------|
| workspace-main/ fallback | `source_candidate()` checks `workspace-main/` and `workspace-assistant/` when `workspace/` is missing |
| accounts.default tokens | New `_get_channel_field()` checks flat path then `accounts.default.*` for all channels |
| TTS edge → microsoft | Checks `providers.microsoft` in addition to `providers.edge`; normalizes back to "edge" for Hermes |
| openclaw.json env keys | Reads `config["env"]` and `config["env"]["vars"]` as additional API key sources |
| API type drift | Adds hyphenated types (`openai-completions`, `anthropic-messages`, `google-generative-ai`), reads `api` field |
| thinkingDefault enum | Maps `minimal`, `xhigh`, `adaptive` to Hermes reasoning_effort |
| Matrix accessToken | Uses `accessToken` instead of `botToken` for Matrix channel |
| SecretRef warnings | file/exec-backed SecretRefs now produce a skip warning instead of silent drop |
| Migration notes | Skills require session restart; WhatsApp requires QR re-pairing |

### Preview-then-confirm UX (`claw.py`)

`hermes claw migrate` now:
1. Shows settings banner
2. Runs a full dry-run preview (no files modified)
3. Displays the preview report
4. If `--dry-run`: stops here
5. Otherwise: asks "Proceed with migration?" (unless `--yes`)
6. Executes the actual migration
7. Offers to archive the source directory

### Docs updates

Updated both `docs/migration/openclaw.md` and `website/docs/guides/migrate-from-openclaw.md`:
- New preview-first UX flow
- workspace-main/ fallback paths
- accounts.default channel token layout
- TTS edge/microsoft rename
- openclaw.json env sub-object as key source
- Hyphenated provider API types
- Matrix accessToken field
- SecretRef warnings
- Skills session restart + WhatsApp re-pairing notes