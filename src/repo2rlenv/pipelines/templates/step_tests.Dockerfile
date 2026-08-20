# Harbor builds the separate verifier environment with this step's tests/ dir
# as the build context. The grader is baked in; the agent never sees this image.
# The agent's tree arrives as the /workspace artifact, so the image only needs
# the toolchain (FROM the bootstrap image) plus the grader files.
FROM ${IMAGE_REF}
# The CTRF plugin is verifier tooling: baked at image build, never installed at
# verify time. This layer is identical across steps, so it caches once per host.
RUN uv pip install --python /opt/venv/bin/python pytest-json-ctrf==0.5.2
COPY . /tests
RUN chmod +x /tests/test.sh
