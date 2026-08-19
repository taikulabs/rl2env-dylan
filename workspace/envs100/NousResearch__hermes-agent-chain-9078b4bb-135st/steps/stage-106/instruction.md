**fix(photon): recover degraded upstream stream (salvage #51105 + #50071)**

## Summary
Recovers Photon iMessage from the silent-inbound failure mode where the sidecar stays alive (HTTP `/healthz` ok, outbound/typing working) but the upstream Spectrum inbound gRPC stream has gone dead — and fixes a wire-channel bug that would have left the **primary** reported scenario unrecovered.

Salvages two contributor PRs onto current `main`:
- **#51105** (@helix4u) — degraded-stream detection + reconnect path
- **#50071** (@SidUParis) — labels upstream CatchUpEvents failures so operators don't chase local allowlist config

## Changes
- `plugins/platforms/photon/sidecar/index.mjs`: track upstream stream health from Spectrum stream logs, expose it via `/healthz`, `process.exit(75)` after sustained degradation so Hermes restarts the adapter; label CatchUpEvents internal errors as upstream-Photon.
- `plugins/platforms/photon/adapter.py`: poll `/healthz`, promote degraded upstream state into a retryable fatal adapter error.
- `gateway/run.py`: reconnect retryable runtime adapter failures immediately instead of waiting the 30s startup retry delay / idle watcher sleep.
- `scripts/release.py`: AUTHOR_MAP entry for @SidUParis.
- Tests: degraded-stream health, `/healthz` stream state, immediate reconnect scheduling, and a new both-console-channels interception regression test.

## The live-test finding (follow-up fix on top)
The detection works by intercepting spectrum-ts's stream log lines. Verified live against the user's pinned **spectrum-ts 3.1.0 + @photon-ai/otel**: `createLogger` routes `severity >= ERROR → console.error` but `WARN/INFO → console.log`. The two lines the monitor keys off land on **different channels**:

| spectrum-ts call | channel | original PR caught it? |
|---|---|---|
| `log.error("stream persistently failing")` | `console.error` | ✅ yes (June 21 rate-limit variant) |
| `log.warn("stream interrupted; reconnecting")` | `console.log` | ❌ **no** (June 22 silent-outage — the *primary* symptom) |

The original interception patched `console.error` only, so the `recovering → degraded` escalation counter never saw the interrupt bursts that dominate the report. Fix: a shared `classifyStreamLog()` fed by **both** `console.error` and `console.log`.

E2E proof (real `@photon-ai/otel` createLogger driving the sidecar logic):

| | Before | After |
|---|---|---|
| 3× real `log.warn("stream interrupted")` | counter stays 0, state never leaves `recovering` | escalates to `degraded` → `exit(75)` → adapter reconnect |

The mocked unit tests (which feed `/healthz` JSON directly) could not catch this — it would have shipped broken for the exact reported scenario.

## Validation
- `node --check plugins/platforms/photon/sidecar/index.mjs` ✅
- `py_compile adapter.py gateway/run.py scripts/release.py` ✅
- `tests/plugins/platforms/photon/{test_overflow_recovery,test_spectrum_patch}.py` + `tests/gateway/test_platform_reconnect.py` → **48 passed**
- Live: spectrum-ts 3.1.0 log-channel routing traced + interrupt-burst escalation confirmed end-to-end

## Credit
- #51105 — @helix4u (degraded-stream recovery), authorship preserved via rebase-merge
- #50071 — @SidUParis (CatchUpEvents labeling), authorship preserved via rebase-merge

, .

Related open cluster on the same symptom (not included here): #49876, #45580, and #50919 (spectrum-ts 3→4 upgrade — would change the log-channel routing and should be evaluated separately).

## Infographic

![Silent Stream Recovery](https://v3b.fal.media/files/b/0a9f6565/prhaP38GXugETAPzFTHb__COVfhMj4.png)