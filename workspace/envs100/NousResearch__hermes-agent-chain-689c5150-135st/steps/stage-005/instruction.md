**feat(nix): container-aware CLI — auto-route into managed container**

## Summary

- When `container.enable = true`, the host `hermes` CLI transparently routes **all** subcommands into the managed Docker/Podman container via `docker exec`
- New `container.hostUsers` option creates a `~/.hermes` symlink bridge to the service stateDir, unifying sessions/config/memories between host and container
- Users in `hostUsers` are auto-added to the `hermes` group
- Retry with spinner on container-down (TTY: 5s, non-TTY: 10s), hard fail instead of silent fallback
- `HERMES_DEV=1` env var bypasses routing for development
- Cleanup on disable: removes symlinks, `.container-mode`, stops service

Depends on #7488 (mautrix migration) for a clean `nix build` — the `atomicwrites` sdist failure from `matrix-nio[e2e]` is resolved there.