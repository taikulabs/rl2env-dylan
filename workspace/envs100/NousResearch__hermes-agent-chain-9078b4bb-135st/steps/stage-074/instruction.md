**feat(skills): add cloudflare-temporary-deploy optional skill**

## Summary
Adds an optional `web-development` skill that teaches the agent to deploy a Cloudflare Worker to a live `workers.dev` URL with **no account, no OAuth, no token** via `wrangler deploy --temporary` (Wrangler 4.102.0+). Cloudflare provisions a throwaway, claimable account valid for 60 minutes — exactly the cheap write→deploy→verify loop autonomous agents need, with no human-in-the-loop hard stop.

Based on Cloudflare's [temporary accounts launch](https://blog.cloudflare.com/temporary-accounts/) (2026-06-19) and the [claim-deployments docs](https://developers.cloudflare.com/workers/platform/claim-deployments/), both read directly rather than trusting the secondary summary that prompted this.

## Changes
- `optional-skills/web-development/cloudflare-temporary-deploy/SKILL.md` — when/when-not, prerequisites (unauthenticated requirement, 4.102.0 version floor), step-by-step deploy + curl-verify flow, product-limits table, pitfalls, verification.
- `.../scripts/parse_deploy_output.py` — stdlib-only parser extracting the live URL, claim URL, account name/state, expiry window, and deploy status from wrangler output; pipeable, has a `--selftest`.
- `tests/skills/test_cloudflare_temporary_deploy_skill.py` — 16 tests including a real-wrangler-output regression case.

## Validation
Verified **live end-to-end** against real Cloudflare (Wrangler 4.103.0), not just mocks:

| Step | Result |
|---|---|
| `wrangler deploy --temporary` (no creds) | `Account: Serene Temple (created)`, live URL + claim URL printed |
| `curl <live_url>` | returned the exact Worker body |
| redeploy | `Account: Serene Temple (reused)`, URL stable |
| parser vs real log | all fields extracted correctly |
| skill test suite | 16/16 passing |

The parser's multi-word-account-name handling was fixed after the live run surfaced `Account: Serene Temple` (the docs sample used a single-token name); a regression test pins it.

## Notes
- Description is 59 chars (≤60 hardline). Lives in `optional-skills/` (niche, Cloudflare-specific), not bundled.
- No new core tool / no dependency — the skill drives the agent's existing `terminal` tool.

## Infographic

![cloudflare-temporary-deploy](https://v3b.fal.media/files/b/0a9f538a/02P8DbpmBMhYZCMORgYdK_tg6lz4Zs.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/skills/test_cloudflare_temporary_deploy_skill.py`