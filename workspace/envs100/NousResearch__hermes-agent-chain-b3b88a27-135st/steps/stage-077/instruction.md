**fix(tui): clickable hyperlinks and skill slash command dispatch**

## Summary

Six TUI fixes across rendering, slash command dispatch, and UX.

### 1. Hyperlinks not clickable (Cmd+Click broken)

**Problem:** Links in TUI markdown responses rendered as colored underlined text only — no OSC 8 hyperlink escape sequences. Cmd+Click does nothing.

**Root cause:** `markdown.tsx` renders `[text](url)` and bare URLs with plain `<Text>` components, discarding the URL. The `<Link>` component from `@hermes/ink` exists and emits proper OSC 8 sequences but was never used.

**Fix:** Import `Link` and wrap all link rendering with it. Added missing `Link` type to `hermes-ink.d.ts`.

### 2. Skill slash commands silently do nothing (`/hermes-agent-dev` → "ready")

**Problem:** Typing `/hermes-agent-dev` does nothing — TUI stays in "ready" state.

**Root cause:** `slash.exec` → `_SlashWorker` → `cli.process_command()` → puts skill message on `_pending_input` Queue that nobody reads in the worker subprocess. `slash.exec` succeeds, so the TUI's `.catch()` → `command.dispatch` (which has correct skill handling) never fires.

**Fix:** Detect skill commands in `slash.exec` early, return error so `command.dispatch` handles them correctly.

### 3. `/plan` slash command silently lost

**Problem:** `/plan` does nothing in the TUI — same `_pending_input` bug as skills.

**Root cause:** Same pattern — `process_command()` builds the plan skill invocation message and queues it on `_pending_input`, which nobody reads in the slash worker.

**Fix:** Intercept `/plan` (and `/retry`, `/queue`, `/steer` as safety nets) in `slash.exec`. Added `command.dispatch` handlers that return a new `{type: 'send', message: ...}` payload. Added `'send'` to `CommandDispatchResponse` type, `asCommandDispatch` parser, and `createSlashHandler` handler.

### 4. Tool results strip ANSI (colors lost)

**Problem:** Tool results from `terminal`, `search_files` etc. lose all color/styling — displayed as plain dim text.

**Root cause:** `messageLine.tsx` unconditionally calls `stripAnsi()` + renders with `<Text>` for tool role messages, even though the `<Ansi>` component is imported and used for assistant messages.

**Fix:** Use `<Ansi>` component when ANSI codes are detected in tool results.

### 5. No terminal tab title

**Problem:** Users with multiple terminal tabs can't identify which tab is running Hermes or whether it's busy.

**Fix:** Added `useTerminalTitle` hook (already exists in `@hermes/ink`, never used) to show `✓ claude-sonnet-4 — Hermes` (ready) or `⏳ claude-sonnet-4 — Hermes` (busy).

### 6. Missing `Link` and `useTerminalTitle` type declarations

The build-time `hermes-ink.d.ts` was missing type declarations for both, causing `tsc -p tsconfig.build.json` to fail.

## Files Changed

| File | Change |
|------|--------|
| `ui-tui/src/components/markdown.tsx` | Wrap links in `<Link>` for OSC 8 hyperlinks |
| `ui-tui/src/components/messageLine.tsx` | Use `<Ansi>` for tool results with ANSI codes |
| `ui-tui/src/app/useMainApp.ts` | Add `useTerminalTitle` for tab title |
| `ui-tui/src/app/createSlashHandler.ts` | Handle `'send'` dispatch type |
| `ui-tui/src/gatewayTypes.ts` | Add `'send'` variant to `CommandDispatchResponse` |
| `ui-tui/src/lib/rpc.ts` | Parse `'send'` in `asCommandDispatch` |
| `ui-tui/src/types/hermes-ink.d.ts` | Add `Link` + `useTerminalTitle` type exports |
| `tui_gateway/server.py` | Intercept `_pending_input` commands + skill commands in `slash.exec`; add `/queue`, `/retry`, `/steer`, `/plan` handlers in `command.dispatch` |
| `ui-tui/src/__tests__/createSlashHandler.test.ts` | Tests: skill dispatch, plan/send dispatch |
| `ui-tui/src/__tests__/asCommandDispatch.test.ts` | Tests: `'send'` type parsing |
| `tests/tui_gateway/test_protocol.py` | Tests: slash.exec interception, command.dispatch handlers |