#!/bin/bash
# Oracle: apply this stage's gold patch. Harbor uploads solution/ for the
# oracle agent only.
set -euxo pipefail
cd /workspace
git config --global --add safe.directory /workspace
PATCH="$(dirname "$0")/patch.diff"
git apply --verbose --reject "$PATCH"
