# Harbor builds the separate verifier environment with this step's tests/ dir
# as the build context. The grader is baked in; the agent never sees this image.
# The agent's tree arrives as the /workspace artifact, so the image only needs
# the toolchain (FROM the bootstrap image) plus the grader files.
FROM local/r2e-bootstrap/nousresearch__hermes-agent:7999ac6e3d59
COPY . /tests
RUN chmod +x /tests/test.sh
