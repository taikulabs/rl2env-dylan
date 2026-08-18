**fix(cron): support per-job runtime overrides**

## Summary
- salvage the per-job cron runtime override fix from PR #1292 onto current main
- honor per-job model, provider, and base_url overrides when cron jobs run
- persist those non-secret overrides in cron job records and expose them through cronjob create/update
- deliberately leave per-job api_key persistence out of scope
- add regression coverage for scheduler behavior and cronjob tool persistence/update paths