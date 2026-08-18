**fix: restore config-saved custom endpoint resolution**

## Summary
- honor config-saved custom endpoint base URLs during main runtime resolution when provider=custom
- route auxiliary text/vision/main-provider resolution through the same custom endpoint logic
- add regression tests for config-only custom endpoint setups