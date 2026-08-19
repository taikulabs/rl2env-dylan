**fix(aux): remove stale session_search model menu entry**

Salvage of #27926 by @hehehe0803.

**What:** `session_search` is now a direct DB-backed tool (FTS5 over conversation history) and no longer uses an auxiliary LLM, so its entry in the `hermes tools` auxiliary-model picker was stale: selecting it had no effect.

**How:** Remove `session_search` from `_AUX_TASKS` in `hermes_cli/main.py`. Test inverted to assert the key is absent.

Original PR: 
.