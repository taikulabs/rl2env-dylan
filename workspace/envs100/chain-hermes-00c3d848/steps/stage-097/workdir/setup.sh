#!/bin/bash
# Harbor step setup for a stage with no carried history.
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
# Sticky invalidation from an earlier failed transition (see the carry
# template): later steps must not grade as clean transitions after one failed.
if [ -f /opt/r2e/episode_invalid.json ]; then
  cp /opt/r2e/episode_invalid.json /workspace/.r2e_carry_degraded.json 2>/dev/null || true
fi
# Install this stage's graded tests. Tests are the specification; the agent
# gets them at their real repository paths.
if [ -d /workspace/.r2e/tests ]; then
  (cd /workspace/.r2e/tests && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "/workspace/.r2e/tests/$rel" "/workspace/$rel"
    done
fi
exit 0
