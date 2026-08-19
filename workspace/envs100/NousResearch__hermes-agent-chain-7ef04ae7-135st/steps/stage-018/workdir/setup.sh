#!/bin/bash
# Harbor step setup for a stage with no carried history.
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
exit 0
