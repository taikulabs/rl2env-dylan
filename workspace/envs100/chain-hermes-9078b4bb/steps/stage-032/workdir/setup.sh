#!/bin/bash
# Harbor step setup for a stage with no carried history.
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
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
