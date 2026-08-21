**fix(cron): tell the user TUI/CLI cron jobs are local-only at create time**

## Summary
Cron jobs created from a TUI or classic-CLI session with `deliver=origin` (or deliver omitted) now tell the user, at create time, that the job is local-only and won't message them — instead of silently running forever with nothing ever delivered.

Root cause: TUI/CLI sessions never populate the `HERMES_SESSION_PLATFORM`/`HERMES_SESSION_CHAT_ID` context vars that `_origin_from_env()` reads, so the job is stored with `origin: null`. The scheduler then resolves no delivery target and (since #43014) deliberately skips delivery — output is saved to `last_output`, but the user only finds out by polling `cronjob(action='list')`. .

This is intentional behavior (local sessions have no live-delivery channel), so the fix surfaces it rather than building a new delivery path.

## Changes
- `tools/cronjob_tools.py`: `cronjob` create appends an informational notice to its result when the created job resolves to **zero** delivery targets and the user did not explicitly request `deliver='local'`. The check delegates to the scheduler's own `_resolve_delivery_targets`, so it correctly accounts for origin, configured home channels, `all`, and explicit `platform:chat` targets — no false positives.
- `agent/prompt_builder.py`: added a `tui` entry to `PLATFORM_HINTS` (the TUI had none) and extended the `cli` hint. Both now tell the agent that cron jobs from these sessions are local-only and that `deliver` must target a gateway-connected platform to notify the user — so the agent stops promising a delivery that never happens.
- Tests: `TestLocalDeliveryNotice` (5 cases) + a platform-hint content assertion.

No scheduler/delivery behavior change, no new env var, and the cron-isolation invariant (cron output is not mirrored into sessions) is untouched.

## Validation
| Scenario (TUI/CLI, no origin) | deliver stored | notice shown |
|---|---|---|
| deliver omitted | `local` | yes |
| deliver=`origin` | `origin` | yes |
| deliver=`local` (explicit) | `local` | no |
| deliver=`telegram:123` | `telegram:123` | no |
| deliver omitted, telegram origin present | `origin` | no |

E2E-verified against a temp `HERMES_HOME` with real `cronjob` create calls; targeted tests pass (16 + sibling cli/media-hint regression tests green).

## Scope note
This is the "fail loud, not silent" fix (the issue's Fix C). The larger Fix A/D — actually round-tripping `deliver=origin` output back into a live TUI session via the existing notification poller — is a separate feature, intentionally not included here.

## Infographic

![cron local-only delivery notice infographic](https://v3b.fal.media/files/b/0a9f8a3a/MBce73d2JUfVptXdyPhJX_J6NT6Fum.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_prompt_builder.py`
- `tests/tools/test_cronjob_tools.py`