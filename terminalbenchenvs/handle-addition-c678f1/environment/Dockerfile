FROM local/r2e-bootstrap/nousresearch__hermes-agent:7999ac6e3d59
WORKDIR /workspace
RUN git config --global --add safe.directory /workspace \
    && git fetch --depth 68 origin 5a1e2a307ae429f075c2565b3cdc267691769c0c 2>/dev/null \
    || git fetch --unshallow origin 2>/dev/null || true
RUN git reset --hard a2847ea7f0a60cc7cbe3faba6716a2f2d52a7efd && git clean -fdx
RUN set -e; git checkout -q -B base a2847ea7f0a60cc7cbe3faba6716a2f2d52a7efd; \
    git remote remove origin 2>/dev/null || true
RUN for ref in $(git branch --format='%(refname:short)' | grep -vx base); do git branch -D "$ref" 2>/dev/null || true; done \
    && git tag -l | xargs -r git tag -d >/dev/null 2>&1 || true \
    && git for-each-ref --format='%(refname)' refs/remotes 2>/dev/null | xargs -r -n1 git update-ref -d 2>/dev/null || true \
    && git reflog expire --expire=now --all 2>/dev/null || true \
    && git gc --prune=now 2>/dev/null || true
COPY spec-tests/ /workspace/
RUN uv pip install --python /opt/venv/bin/python pytest-json-ctrf==0.5.2
ENV PYTHONDONTWRITEBYTECODE=1
