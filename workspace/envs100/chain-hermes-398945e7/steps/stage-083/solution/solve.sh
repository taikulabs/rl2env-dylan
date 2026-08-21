#!/bin/bash
# Oracle: apply this stage's gold patch. Harbor uploads solution/ for the
# oracle agent only.
set -euxo pipefail
cd /workspace
git config --global --add safe.directory /workspace
PATCH="$(dirname "$0")/patch.diff"
# The workspace tests were installed at this stage's gold version by setup, so
# their hunks are already present; a clean 3-way handles those, and anything
# left over is reject noise that must not leak into the next step's carry check.
git apply --verbose "$PATCH" \
  || git apply --verbose --3way "$PATCH" \
  || git apply --verbose --reject "$PATCH" \
  || true
find . -name '*.rej' -delete 2>/dev/null || true
