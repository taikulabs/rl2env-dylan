# Sustained development on `NousResearch/hermes-agent`

You are working in `/workspace`, a checkout of `NousResearch/hermes-agent` at commit `556e0f4b4326`.

Ahead of you are **111 stages** of real development history for the `(root)` area of this codebase. Each stage is one change that was actually made to this project, and each is graded by that change's own tests.

## How to work

```bash
chain status     # show the current stage and what it must achieve
chain submit     # grade the current stage and open the next one
chain log        # review what you have completed so far
```

Start with `chain status`. Implement the stage in the repository, then run `chain submit`. If the stage's tests do not pass, `chain submit` tells you which ones failed so you can iterate. When a stage will not converge, `chain submit --force` moves on and keeps whatever partial credit you earned.

## How you are scored

Your reward is the mean of the per-stage scores, so **every stage you land adds to it** — a partial run is worth more than an abandoned one.

Scoring happens against the repository as you finally leave it, and every stage's tests are re-run then. Work must therefore *accumulate*: do not undo an earlier stage to make a later one pass. Test files are restored from the project's own history before grading, so editing or deleting a test cannot raise your score.

Some stages arrive with unrelated project churn already applied for you (formatting sweeps, dependency bumps). That is deliberate and needs no action from you.