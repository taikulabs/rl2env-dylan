#!/bin/bash
# Harbor step setup: hygiene + transactional carry + test installation.
# Runs in the agent environment before the agent phase.
set -uo pipefail
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
# Sticky invalidation: a carry that failed at an earlier step must keep every
# later step from grading as a clean transition. The marker lives outside the
# workspace so no step payload can erase it, and every setup re-arms it.
if [ -f /opt/r2e/episode_invalid.json ]; then
  cp /opt/r2e/episode_invalid.json /workspace/.r2e_carry_degraded.json 2>/dev/null || true
fi
cd /workspace || exit 1
git config --global --add safe.directory /workspace
CARRY="$(dirname "$0")/carry.diff"

VALID=1
if [ -s "$CARRY" ]; then
  # Clear reject leftovers from earlier steps (e.g. the oracle's solve.sh):
  # only rejects produced by THIS carry count.
  find . -name '*.rej' -delete 2>/dev/null || true
  # Only clean paths are acceptable: normal apply, or a full three-way apply.
  # --reject is deliberately absent — partial application is not a transition.
  if git apply --verbose "$CARRY" || git apply --verbose --3way "$CARRY"; then
    # A "successful" apply still fails if it left conflict residue.
    if find . -name '*.rej' -print -quit | grep -q . || [ -n "$(git ls-files -u)" ]; then
      VALID=0
    fi
    # git diff --check is intentionally NOT used: real history contains
    # whitespace warnings, and this check would false-fail valid transitions.
  else
    VALID=0
  fi
fi

if [ "$VALID" != "1" ]; then
  # Tolerated merge, not a rollback: the tests are the arbiter of the tree.
  # Measured driver: rolling back on agent-vs-churn conflicts cascaded
  # invalidation across every later step and scored Opus 0.03 over 33 steps,
  # while the oracle (clean applies) scores ~1.0. Grading the merged tree and
  # flagging the degrade as telemetry keeps both properties: no free reward
  # (the nop still scores 0 — its tests fail), and no silent hybrid.
  git apply --verbose --reject "$CARRY" || true
  find . -name '*.rej' -delete 2>/dev/null || true
  mkdir -p /opt/r2e
  printf '{"degraded": true, "phase": "setup", "reason": "carry merged with rejects; graded by tests"}\n' \
    > /opt/r2e/episode_invalid.json
  cp /opt/r2e/episode_invalid.json /workspace/.r2e_carry_degraded.json
fi

# Install this stage's graded tests AFTER the carry, on every path — a stage
# must never hand over the workspace without the tests its prompt promises.
if [ -d /workspace/.r2e/tests ]; then
  (cd /workspace/.r2e/tests && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "/workspace/.r2e/tests/$rel" "/workspace/$rel"
    done
fi
exit 0
