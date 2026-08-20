**fix(computer-use): working vision capture + whole-screen/desktop target on Windows**

## Summary
Windows computer_use can now both (1) take a working `vision` screenshot and (2) capture the whole screen / taskbar — two distinct failures a user hit on Desktop and Telegram.

Two root causes:
- **`vision` mode returned 0x0.** cua-driver 0.6.x removed the standalone `screenshot` MCP tool, so `capture(mode='vision')` hit `Unknown tool: screenshot` and returned no PNG (som/ax kept working because they use `get_window_state`). Salvaged from #50771 (@jeeves-assistant); same fix submitted earlier as #39262 (@Tranquil-Flow).
- **No whole-screen / desktop capture path.** `capture()` only ever matched *application* windows, and the schema advertised "or the whole screen" without any code delivering it — so "show me my 2 screens" and "click the taskbar" couldn't work (the taskbar isn't an app window).

## Changes
- `cua_backend.py`: route `vision` capture through `get_window_state(capture_mode='vision')`; add `capture(app='screen'|'desktop'|'fullscreen'|'all')` that resolves to the OS shell/desktop window (Windows `Progman`/`WorkerW` desktop, `Shell_TrayWnd` taskbar; macOS Finder/Dock), preferring the desktop backdrop over the taskbar. No-desktop-window path returns a clear message instead of silently grabbing the frontmost app.
- `schema.py`: document `app='screen'`/`'desktop'` and state the per-window / single-monitor capture limit.
- `tests/tools/test_computer_use.py`: vision-routing regression test + screen-target hit/miss tests.
- `scripts/release.py`: AUTHOR_MAP entry for @jeeves-assistant.

## Limitation (honest)
cua-driver is window-oriented — there is no MCP tool that captures the entire virtual desktop or an arbitrary monitor as one image. A single capture still can't span multiple monitors; the schema now says so. "Both screens at once" means one display/window at a time.

## Validation
`tests/tools/test_computer_use.py` — 167 passed (3 new, no regressions).

| | Before | After |
|---|---|---|
| `capture(mode='vision')` | `Unknown tool: screenshot` → 0x0, no PNG | routed via `get_window_state` → real PNG |
| `capture(app='screen')` | matched no app → empty | targets desktop window (Progman/Finder) |
| `capture(app='desktop')`, no shell window | silent frontmost-app grab | clear per-window-limit message |

, #39262.

## Infographic
![Computer use Windows capture fix](https://v3b.fal.media/files/b/0a9f5ac3/BhpowNhl6YggREn3tHElq_Y2rutQNP.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_computer_use.py`