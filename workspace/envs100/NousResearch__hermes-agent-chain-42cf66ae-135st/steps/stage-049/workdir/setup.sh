#!/bin/bash
set -uo pipefail
# Remove the previous step's grader before the agent starts.
rm -rf /logs/verifier /tests 2>/dev/null || true
cd /workspace
git config --global --add safe.directory /workspace
CARRY="$(dirname "$0")/carry.diff"
[ -s "$CARRY" ] || exit 0
# Tolerate hunks already present: an agent may have written equivalent
# code, and a partly-applied carry is better than a failed step setup.
git apply --verbose "$CARRY" \
  || git apply --verbose --3way "$CARRY" \
  || git apply --verbose --reject "$CARRY" \
  || true
exit 0
