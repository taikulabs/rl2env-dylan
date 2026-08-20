# Sustained development on `NousResearch/hermes-agent`

You are working in `/workspace`, a checkout of `NousResearch/hermes-agent` at commit `7ef04ae7a799`.

Ahead of you are **108 stages** of real development history for the `agent` area of this codebase. Each stage is one change that was actually made to this project, and each is graded by that change's own tests.

## How each stage works

The environment runs one stage at a time. When a stage opens you receive its objective. Implement the change in `/workspace` — edit the source and run the tests yourself while you work. When you are done, end your turn: the environment then runs that stage's tests in a fresh environment, records the score, and opens the next stage. You do not need to commit anything; the workspace itself is graded.

The workspace persists between stages, so later stages build on your earlier work. Reverting earlier work can make a later stage ungradeable — build forward.

## How you are scored

Each stage is graded independently by that stage's own tests. A stage pays only when its full test command passes cleanly — all graded tests green, nothing else broken. Your reward is the mean of the per-stage scores, so **every stage you land adds to it** — a partial run is worth more than an abandoned one.

Test files are restored from the project's own history before grading, and grading runs in a fresh environment, so editing or deleting a test cannot raise your score.

Some stages arrive with unrelated project churn already applied for you (formatting sweeps, dependency bumps). That is deliberate and needs no action from you.