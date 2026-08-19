**feat: entry-level Podman support — find_docker() + rootless entrypoint**

## Summary

Adds basic Podman compatibility in two areas:

### 1. Container runtime discovery (`find_docker()`)
- **`HERMES_DOCKER_BINARY` env var** — explicit override for the container binary (e.g. `/usr/bin/podman`). Checked first, before any PATH resolution.
- **`podman` on PATH** — automatic fallback when `docker` isn't found. Docker is still preferred when both are available.
- Resolution order: env var override → docker on PATH → podman on PATH → macOS known locations

### 2. Rootless Podman entrypoint fixes (`docker/entrypoint.sh`)
- **Respect `HERMES_HOME` env var** — was hardcoded to `/opt/data`, now uses `${HERMES_HOME:-/opt/data}`
- **GID conflict tolerance** — `groupmod -o` allows non-unique GIDs (fixes macOS GID 20 "staff" colliding with Debian's "dialout" group)
- **Best-effort `chown`** — in rootless Podman the container's fakeroot can't actually chown mounted volumes. Now logs a warning and continues instead of failing with "Operation not permitted"

### Context
Discord user reported being unable to start hermes at all under Podman on macOS. The `chown` failure in the entrypoint was a hard block. This unblocks that use case.

Based on work by @alanjds (PR #3996) and @malaiwah (PR #8115).
.