**fix(cron): persist cron sessions to SQLite**

## Summary
- cherry-pick the substantive fix from #907 so cron-created agents pass `session_db` and become recallable via SQLite/session_search
- tag persisted cron-run sessions with `source=cron` instead of falling back to `cli`
- close the per-run SessionDB and add regression coverage for cron session wiring

## Contributor credit
- cherry-picked Ömer Kaz's commit from #907 with authorship preserved
- added a small follow-up commit for cron source tagging and tests