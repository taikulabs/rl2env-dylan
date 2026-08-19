**fix(telegram): check updater/app state before disconnect**

## Summary
- 
- preserve graceful shutdown by always calling `shutdown()` once the adapter exists
- add a regression test covering disconnect with an inactive updater/app so shutdown stays quiet and completes cleanly
