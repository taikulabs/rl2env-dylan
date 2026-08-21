#!/bin/bash
# Harbor step setup: hygiene + transactional carry + test installation.
# Runs in the agent environment before the agent phase.
set -uo pipefail
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
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
  # Tolerated merge: --reject applies every hunk it can and writes .rej files
  # for the rest. The flag means real content loss (churn that did not land),
  # not merely "the agent diverged from history" — divergence is normal and
  # the tests are the arbiter. (3way never works here by construction: the
  # image scrub prunes the carry's pre-image blobs.)
  git apply --verbose --reject "$CARRY" || true
  REJ_COUNT=$(find . -name '*.rej' | wc -l | tr -d ' ')
  if [ "$REJ_COUNT" != "0" ]; then
    printf '{"degraded": true, "phase": "setup", "reason": "carry hunks rejected; content lost", "rej_files": %s}\n' \
      "$REJ_COUNT" > /workspace/.r2e_carry_degraded.json
  fi
  find . -name '*.rej' -delete 2>/dev/null || true
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
