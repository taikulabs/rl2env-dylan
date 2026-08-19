**feat(background-review): aux-model routing + context digest + adaptive cadence to cut self-improvement cost**

## Summary

Adds an **aux-model selector for the background self-improvement review** — the post-turn fork that decides whether to save a memory or patch a skill. By default it runs on your main chat model; this lets you point it at a cheaper one.

`auxiliary.background_review.{provider,model}` (default `auto` = main chat model). Set it to a cheaper model and the review runs there for a large cost cut, at **some** quality cost — on a real session Haiku captured a bit less than Opus (details below). **Nothing changes unless you opt in** — leave it `auto` and the review behaves exactly as today.

## The one design decision: the prompt cache

Your main chat is already **warm** in the prompt cache, so the review's default full-history replay on the main model is cheap cache **reads**. That's optimal and left untouched. A *different* model can't reuse that cache (different key), so a routed review is "cold" regardless — replaying the full transcript would just cold-write it all. So the policy is simply:

- **Review on the same model as your agent (default `auto`)** → replay the full history. Warm cache reads. Unchanged.
- **Review on a different (cheaper) model** → replay a compact **digest** (recent turns verbatim + a summary of older ones). The cache is cold either way, so writing fewer tokens is a pure win.

That's the whole feature: same model → full replay; different model → digest. Decided automatically by whether the configured review model differs from the main model.

## What changed

- `agent/background_review.py` — `_resolve_review_runtime()` (the selector; `routed=False` for auto/same-model, `routed=True` for a configured different model, with credential resolution and the codex_app_server→codex_responses downgrade preserved). `_digest_history()` builds the compact replay, used **only** on the routed path. The fork shares the parent's warm cached system prompt only when not routed.
- `hermes_cli/config.py` — the `auxiliary.background_review` block (provider/model/base_url/api_key/timeout/extra_body), default `auto`.
- `website/docs/user-guide/features/memory.md` — a short section documenting the selector.
- Tests — `_resolve_review_runtime` (auto/same/different/failure) and `_digest_history` (tail preservation, alternation safety, arc capture).

No changes to cadence, no budget guards, no pre-pass, no default behavior — just the selector and the routed-digest it implies.

## Validation

Benchmarked live against Anthropic (Opus main chat; review on Opus vs Haiku), per-signal capture scored separately for skill and memory.

**Real-session test (the honest headline).** Reconstructed this PR's own build conversation (~102K tokens, real corrections buried under benchmark/CI/infographic tool-noise), 5 ground-truth durable signals (3 skill, 2 memory), 2 reps:

| | skill | memory | cost / review |
|---|---|---|---|
| Opus full (default) | 5/6 | 4/4 | ~$3.34 |
| Haiku digest (routed) | **4/6** | **3/4** | **~$0.086 (~39×)** |

On a real messy session **Haiku is weaker than Opus on both dimensions** — it dropped one skill and one memory — at ~39× lower cost. It's a real quality-for-cost trade, not a free lunch. Capture isn't perfect for *either* model on a buried real session (full Opus missed a skill in 1 of 2 reps too); the hardest signal — a diffuse "verify premises before claiming" meta-lesson spread across many corrections — was missed by Haiku both reps and Opus once.

**Synthetic scenarios (cleaner, for reference).** On 7 hand-built scenarios with signals less deeply buried, the gap narrows: Opus 12/12 skill, 9/9 memory vs Haiku 11/12 skill, 9/9 memory, and Haiku was actually *cleaner* on a retracted-distractor (0/6 vs 3/6 false-saves). So the weaker real-session numbers are the conservative end of the range.

Harnesses, scenarios, raw results, and the cache-cost recompute are published:
**https://gist.github.com/teknium1/e02488adbbaac0cbc9c793e84f4a06c2**

**Verdict:** routing is a large cost cut (~39× on this real sessio

…(truncated)