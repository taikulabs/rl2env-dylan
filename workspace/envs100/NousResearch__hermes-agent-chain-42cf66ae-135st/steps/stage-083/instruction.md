**fix: verify crontab availability for cronjob tools**

## Summary
- 
- add regression tests covering both missing and present `crontab` binaries in interactive mode
- include the missing `shutil` import needed by the salvaged change
