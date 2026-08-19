**fix: is_local_endpoint misses Docker/Podman DNS names**

## Summary

`is_local_endpoint()` in `agent/model_metadata.py` only recognized `localhost`, loopback IPs, and RFC-1918 addresses. Container runtime DNS names that resolve to the host machine were missed:

- `host.docker.internal` (Docker)
- `gateway.docker.internal` (Docker bridge)
- `host.containers.internal` (Podman)
- `host.lima.internal` (Lima/colima on macOS)

Users running Ollama on the host with the agent inside Docker/Podman got the default 120s stream read timeout instead of the auto-bumped 1800s, causing premature connection kills during long prefill phases.

## Changes

- `agent/model_metadata.py`: Added `_CONTAINER_LOCAL_SUFFIXES` tuple and a suffix check in `is_local_endpoint()`, placed right after the `_LOCAL_HOSTS` exact-match check.
- `tests/agent/test_local_stream_timeout.py`: Added container DNS names to the stream timeout parametrize list + new `TestIsLocalEndpoint` class with direct unit tests covering classic addresses, container DNS names, and remote endpoints (including a negative case for `evil.docker.internal.example.com`).