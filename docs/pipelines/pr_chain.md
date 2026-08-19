# `pr_chain`

Long-horizon environments: **one task per contiguous run of a repository's
history**. Each retained stage ends on a real pull request and becomes one
native Harbor step. For each step, Harbor applies the setup, gives the
instruction to the agent, runs the verifier, and records the reward. The task
reward is the mean of all completed step rewards.

`pr_chain` studies planning, state carry, and recovery across many verified
milestones. Every emitted training task contains at least **100 native Harbor
steps**. The options model rejects a lower `min_steps` value. Selection adds
headroom for stages that validation can drop, and emission checks the final
step count again. Reward checkpoints cannot terminate an episode before step
100.

| | |
|---|---|
| Status | **experimental (v0.9)** |
| Sandbox required at gen | Yes — Docker via the [bootstrap phase](../reference/BOOTSTRAP.md) |
| LLM required at gen | No |
| Reward kinds emitted | `test_execution` |
| Source | GitHub · GitLab (needs pull requests) |
| Design doc | [RFC 0011](../rfcs/0011-pr-chain.md) |

## Why chains are built from history, not from similar PRs

The obvious way to build a longer task is to pick several PRs that touch the same
subsystem and concatenate them. It does not work: **a PR's diff only applies to
the tree it was written against.** Pick PRs #100, #400 and #900 and #400's patch
will not apply on top of #100's, because the merges in between moved the code
underneath it.

`pr_chain` therefore uses the one ordering that is replayable by construction: the
**first-parent history** of the default branch. `git diff <c>^1 <c>` is exactly
the change the branch received at step `c`, whether the project squash-merges,
merge-commits or pushes directly. Replaying consecutive steps reproduces history,
so every intermediate tree is a real commit that really passed CI.

```
base ─[carry]─▶ c1^ ─[goal 1]─▶ c1 ─[carry]─▶ c2^ ─[goal 2]─▶ c2 ─▶ ...
```

- **Anchor** — a step whose diff touches both source *and* test files, so a
  fail-to-pass oracle can exist. Its change is the stage's **goal**: what the
  agent implements.
- **Carry** — steps that cannot anchor a stage (formatting sweeps, dependency
  bumps, docs). The environment applies these **for free** when the stage opens.

Carry keeps the partition gapless *and* fair: no history is skipped, so stage k+1
starts from a real commit, yet the agent is never asked to reproduce
`npm run fix` output. A carry over budget becomes a barrier that no chain crosses.

Coherence — the share of a chain's stages in one subsystem — is applied as a
**filter** (`min_coherence`), not as a ranking. Ranking by coherence strands short
runs between picks and loses chains without meaningfully raising coherence.

## What the agent sees

Harbor reveals one stage at a time:

1. `steps/<name>/workdir/setup.sh` applies ungraded history before the step.
2. `steps/<name>/instruction.md` gives the current PR objective.
3. The agent changes the persistent `/workspace` tree.
4. `steps/<name>/tests/test.sh` restores the graded tests and returns the step
   reward.

The next instruction and its tests do not enter the agent environment before
that step. The workspace persists, so later objectives build on earlier work.

## Task shape

```
<owner>__<repo>-chain-<base8>-<N>st/
├── task.toml                       # 100+ [[steps]] entries
├── instruction.md                  # task-level protocol
├── environment/Dockerfile          # tree at the chain base
├── environment/docker-compose.yaml # egress guard
├── chain/plan.json                 # inspectable stage plan
├── steps/
│   ├── stage-001/
│   │   ├── instruction.md
│   │   ├── workdir/setup.sh        # applies carry before the agent runs
│   │   ├── tests/test.sh           # F2P/P2P verifier entry point
│   │   └── solution/solve.sh       # available only to the oracle agent
│   └── stage-100/...
└── solution/patch.diff             # whole-chain oracle
```

Harbor uploads the files for the current step. The Docker image contains only
the base repository and its toolchain. No chain payload is encoded in a Docker
layer.

## Reward

```
step_reward = f2p_rate × p2p_rate   if the test command is clean (exit 0, no untracked failures)
            = 0                     otherwise
task_reward = mean(completed step rewards)
```

A stage pays only on a clean command: validation keeps stages whose gold run is
clean, so the gate never blocks earnable work, and an agent cannot keep partial
credit while damaging neighbouring tests. The tracked F2P×P2P product is still
reported as a diagnostic (`tracked_score`). A carry that only partially applies
fails the step closed as an infrastructure result (`invalid_transition`), not a
gradeable agent attempt. Each verifier restores its test files before it runs,
so an agent cannot raise the score by changing or deleting tests.

Validation checks each oracle on four real trees: chain base, stage start,
stage gold, and chain head. A FAIL_TO_PASS test must fail on both pre-change
trees and pass on both post-change trees. This rejects a free stage and keeps
the whole-chain oracle valid.

`min_reward` checkpoints are **disabled by default**: Harbor's multi-step mean
divides by *executed* steps only, so an agent that is ahead on average could
tank a checkpoint step to end the run and lock in that average
(harbor-framework/harbor#2783). `--pipeline-opt hopeless_checkpoint_every=25`
opts in for cost control; checkpoints then start at step `min_steps`, so no
early stop ever cuts the promised minimum horizon.

## Options

```bash
repo2rlenv generate --repo NousResearch/hermes-agent --pipeline pr_chain \
  --pipeline-opt limit=500 \
  --pipeline-opt min_steps=100 \
  --pipeline-opt max_steps=200 \
  --pipeline-opt min_coherence=0.25 \
  --force-language python \
  --out ./datasets/hermes-chain
```

| Option | Default | Meaning |
|---|---|---|
| `limit` | 10 | chains to emit; scale out with extra workers over the same selection — the stage-validation cache dedupes their work |
| `min_steps` | 100 | hard minimum native Harbor steps; lower values are invalid |
| `max_steps` | 200 | maximum selected stages before validation |
| `step_margin` | 1.35 | selection headroom for stages that validation can drop |
| `min_coherence` | 0.25 | share of stages in the dominant subsystem |
| `require_pr_link` | true | require a resolvable PR number for every stage |
| `max_carry_steps` | 25 | free history that setup can replay per stage |
| `max_carry_lines` | 60000 | carry limit by changed lines |
| `overlap_ladder` | `[0.0, 0.25, 0.5]` | allowed stage-reuse levels |
| `step_agent_timeout_sec` | 3600 | agent limit for one step |
| `step_verifier_timeout_sec` | 900 | verifier limit for one step |
| `hopeless_checkpoint_every` | 0 | abort interval, starting at `min_steps`; 0 (default) disables it — see the reward note |

## Yield

Disjoint yield is arithmetic: `gated_stages / stages_per_chain`. Asking for more
climbs the overlap ladder rather than silently returning fewer chains, and the
rung actually used is reported in the run summary.

Measured on `NousResearch/hermes-agent`:

| Quantity | Value |
|---|---|
| PRs harvested | 65,944 |
| First-parent history steps | 19,072 |
| PR-anchored gated stages | 5,886 in 36 segments |
| Candidate windows at the padded 100-step target | 1,459 |
| Selected disjoint chains at `min_coherence=0.25` | 22 |
| Verified example A | 121 native steps |
| Verified example B | 111 native steps |
| First verified chain per shard | about 4,352 seconds with two workers |
| Oracle run, 111-step chain | **111/111 steps at 1.0** (Harbor oracle agent, separate verifier env per step) |
| Null run, same chain | 100/100 steps at 0.0; abort gate fired at step 100 |

Validation runs each stage's target tests on four real trees. This is the main
generation cost. A durable per-stage cache
(`.r2e_cache/bootstrap/chain_validation_cache.sqlite`) makes restarts free and
lets extra workers over the same selection divide the work: each stage is
validated once globally, whichever worker reaches it first, and emission is
deterministic so duplicate completions are harmless. Legacy chain-level
sharding (`shard_index`/`shard_count`) remains for strictly disjoint batches.

## Anti-contamination

- The working tree sits at the chain's base commit and the git history is then
  scrubbed, so no future commit — and therefore no stage's fix — is reachable
  from `.git`. Verified on a built image: the chain head and stage-2 gold commits
  are both pruned and only `refs/heads/base` survives.
- The egress guard blackholes the fix-bearing hosts (PyPI, GitHub and their CDNs).
- Test files are **copied** over the tree before grading, so editing or deleting a
  test cannot raise the score.
- Harbor uploads each stage's gold source diff only for an oracle-agent run. A
  normal agent receives the instruction and test payload, but not the solution.
- Grading runs in a **separate verifier environment** per step
  (`separate_verifier`, default on): Harbor builds it from the step's
  `tests/Dockerfile` and the agent's tree crosses over only as a `/workspace`
  artifact (VCS and cache dirs excluded). A root agent cannot tamper with the
  grader's interpreter, PATH, or reward files there. Two known limitations:
  agent-deleted files still exist in the fresh image (artifact upload is a
  merge, not a sync), and the transfer costs one image build plus one workspace
  copy per step. Disable only for throwaway training runs.
- In shared mode the step scripts still assume a hostile workspace: planted
  `conftest.py` files on the collection path are purged and the gold harness
  (conftests, pytest config) is restored before grading; the grader runs under
  `python3 -S`; and an unparseable test log scores 0.0 whenever an F2P oracle
  exists. One residual remains shared-mode-only: an agent-spawned background
  process could race the reward file write. There is no safe in-container kill
  (Harbor's own helpers also show PPID 1, and killing one broke the exec
  channel) — the separate verifier environment is the boundary for that.
- The compose denylist is always emitted and works on every Docker host. A
  stronger default-deny posture is available with
  `--pipeline-opt egress_allowlist=true`: `[environment]
  network_mode="allowlist"` permits only the model API and harness registries,
  and the verifier phase runs `no-network`. It requires a host kernel with
  nftables fib inet support — Harbor *rejects the task at load time* when the
  host cannot enforce the policy (Docker Desktop's VM cannot), so it stays
  opt-in rather than making tasks unloadable on developer workstations.

## Environment requirements

**This is where a chain dataset is most likely to go quietly wrong.** A chain
resets the tree to historical commits, so the bootstrap image must satisfy the
**union** of what those commits need, not just HEAD's. When it does not, pytest
fails *collection* — which the log parser sees as a single error and the oracle
reads as "every test in this stage failed". The stage silently loses its oracle
and the chain quietly shrinks. Three concrete instances on hermes-agent:

1. **Eagerly-imported optional providers.** At older commits
   `tools/web_tools.py` imports `firecrawl` at module scope; HEAD made it lazy.
   The project's own `all` extra deliberately *excludes* those providers by
   policy, so `--extra all` does not help — `uv sync --all-extras` does. Fixing
   this alone took stage survival on the measured chain from 7/24 to 20/24.
2. **Interpreter version.** `.python-version` pins 3.11, and the `wake` extra
   pulls `tflite-runtime`, which ships cp311 wheels only. A 3.12 image cannot
   install the full extra set.
3. **Dropped pytest plugins.** Older `pyproject.toml` revisions set
   `addopts = "-m 'not integration' -n auto"` and pinned `pytest-xdist`, which
   HEAD later removed — a HEAD-only install dies on
   `pytest: error: unrecognized arguments: -n`. Install the plugins and pass
   `-n 0` in `BootstrapSpec.test_cmds` so output stays in the single-worker
   format the log parser reads.

Note also that test commands run through `bash -lc`, a login shell that re-reads
`/etc/profile` and discards `ENV PATH`. An image whose toolchain lives in a
virtualenv must expose it via `/etc/profile.d`, not `ENV PATH` alone.

The working recipe for this repository is in
[`workspace/hermes-agent.Dockerfile`](https://github.com/huggingface/Repo2RLEnv);
`BootstrapSpec.user_dockerfile` + `BootstrapSpec.test_cmds` feed it to the
bootstrap phase with no LLM agent involved.

## Limitations

- **Only merged PRs can gate a stage.** Open and closed-unmerged PRs have no
  verified merge, so no fail-to-pass oracle can be derived from them. They are
  harvested into the corpus and remain available for future diff-graded stages.
- **Coherence has a low ceiling at this horizon.** A 100-step chain spans many
  parts of a repository. On `hermes-agent`, 22 disjoint chains pass a 0.25
  coherence floor, but only two pass 0.4. Measure capacity before you raise this
  option.
- **PASS_TO_PASS is per-stage.** It is computed over the stage's own targeted test
  files, so a stage that adds a brand-new test file has none. That is why
  `min_pass_to_pass_per_stage` defaults to 0 and the count is reported instead.
- **Stage instructions are not rewritten.** A stage's objective is its PR title
  plus a leak-stripped body; `min_instruction_words` drops the ones with no real
  problem statement rather than synthesizing one.
