FROM local/r2e-bootstrap/nousresearch__hermes-agent:7999ac6e3d59
WORKDIR /workspace
RUN git config --global --add safe.directory /workspace \
    && git fetch --depth 68 origin bd7e272c1fd61d570f64845625827c5a99d69c14 2>/dev/null \
    || git fetch --unshallow origin 2>/dev/null || true
RUN git reset --hard 4093982f19578008a5aefd8f4c1dac971ec9286d && git clean -fdx
RUN set -e; git checkout -q -B base 4093982f19578008a5aefd8f4c1dac971ec9286d; \
    git remote remove origin 2>/dev/null || true
RUN for ref in $(git branch --format='%(refname:short)' | grep -vx base); do git branch -D "$ref" 2>/dev/null || true; done \
    && git tag -l | xargs -r git tag -d >/dev/null 2>&1 || true \
    && git for-each-ref --format='%(refname)' refs/remotes 2>/dev/null | xargs -r -n1 git update-ref -d 2>/dev/null || true \
    && git reflog expire --expire=now --all 2>/dev/null || true \
    && git gc --prune=now 2>/dev/null || true
COPY spec-tests/ /workspace/
RUN uv pip install --python /opt/venv/bin/python pytest-json-ctrf==0.5.2
ENV PYTHONDONTWRITEBYTECODE=1
