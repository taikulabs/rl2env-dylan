FROM local/r2e-bootstrap/nousresearch__hermes-agent:7999ac6e3d59
WORKDIR /workspace
RUN git config --global --add safe.directory /workspace \
    && git fetch --depth 64 origin 779f8df6a6c2a3fc63d2b2e8754e64fc9c3754dd 2>/dev/null \
    || git fetch --unshallow origin 2>/dev/null || true
RUN git reset --hard fd0e1aac728b259d04e93b737228c48b0597e081 && git clean -fdx
RUN set -e; git checkout -q -B base fd0e1aac728b259d04e93b737228c48b0597e081; \
    git remote remove origin 2>/dev/null || true
RUN for ref in $(git branch --format='%(refname:short)' | grep -vx base); do git branch -D "$ref" 2>/dev/null || true; done \
    && git tag -l | xargs -r git tag -d >/dev/null 2>&1 || true \
    && git for-each-ref --format='%(refname)' refs/remotes 2>/dev/null | xargs -r -n1 git update-ref -d 2>/dev/null || true \
    && git reflog expire --expire=now --all 2>/dev/null || true \
    && git gc --prune=now 2>/dev/null || true
COPY spec-tests/ /workspace/
RUN uv pip install --python /opt/venv/bin/python pytest-json-ctrf==0.5.2
ENV PYTHONDONTWRITEBYTECODE=1
