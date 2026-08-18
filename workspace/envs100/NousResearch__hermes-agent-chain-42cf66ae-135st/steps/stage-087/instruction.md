**fix(telegram): check updater/app state before disconnect**

## Summary
- cherry-pick the substantive fix from #1197 so Telegram disconnect only stops the updater and app when they are actually running
- preserve graceful shutdown by always calling `shutdown()` once the adapter exists
- add a regression test covering disconnect with an inactive updater/app so shutdown stays quiet and completes cleanly