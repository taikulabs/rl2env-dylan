#!/bin/bash
# Harbor step setup for a stage with no carried history.
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
# Place this stage's graded tests (staged by the step's workdir upload) after
# the carry, so a carry that touched the same files cannot clobber them.
if [ -d /workspace/.r2e/tests ]; then
  (cd /workspace/.r2e/tests && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "/workspace/.r2e/tests/$rel" "/workspace/$rel"
    done
fi
exit 0
