**fix: verify crontab availability for cronjob tools**

## Summary
- cherry-pick the substantive cronjob availability check from #1380 so cronjob tools only appear when `crontab` is actually installed
- add regression tests covering both missing and present `crontab` binaries in interactive mode
- include the missing `shutil` import needed by the salvaged change