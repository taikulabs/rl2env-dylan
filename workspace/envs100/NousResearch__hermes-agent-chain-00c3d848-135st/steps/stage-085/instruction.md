**Add GMI Cloud as a first-class API-key provider**

## Summary

- add GMI Cloud as a first-class API-key provider with built-in auth, aliases, provider overlays, model catalog wiring, and CLI entry points
- wire GMI into doctor/config/env-var/docs flows and add focused regression coverage for provider resolution, model metadata, CLI flow, and auxiliary routing
- preserve GMI context-length resolution from its live `/v1/models` metadata and fix cached auxiliary client handling for slash-form model overrides