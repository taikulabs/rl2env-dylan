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

# Snapshot the tree so a failed carry rolls back atomically: the workspace is
# never handed to the agent in a half-patched state the oracle never saw.
# The snapshot commit lives on top of the scrubbed base and contains only the
# agent's own prior work — no future history is reachable from it.
git add -A
git -c user.email=r2e@local -c user.name=r2e commit -qm "step setup snapshot" \
  --allow-empty --no-verify
PRE="$(git rev-parse HEAD)"

VALID=1
if [ -s "$CARRY" ]; then
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
  # Roll back: the agent sees the pre-carry tree, never the hybrid. The marker
  # outside /workspace makes the invalidation sticky across later setups; the
  # workspace copy crosses into the verifier environment with the artifact, so
  # grading can flag the step as an invalid transition instead of an agent try.
  git reset --hard "$PRE" >/dev/null 2>&1 || true
  mkdir -p /opt/r2e
  printf '{"degraded": true, "phase": "setup", "reason": "carry did not apply cleanly; rolled back"}\n' \
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
