#!/bin/bash
# Remove the previous step's grader before the agent starts.
rm -rf /logs/verifier /tests 2>/dev/null || true
# No carried history for this step.
exit 0
