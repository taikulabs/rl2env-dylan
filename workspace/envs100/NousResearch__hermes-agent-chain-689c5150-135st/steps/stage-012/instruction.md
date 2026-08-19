**feat: add network.force_ipv4 config to fix IPv6 timeout issues**

## Summary

On servers with broken or unreachable IPv6, Python's `socket.getaddrinfo()` returns AAAA records first. All HTTP libraries (httpx, requests, urllib, the OpenAI SDK) try IPv6 connections and hang for the full TCP timeout before falling back to IPv4.

**Symptom:** web_extract, web_search, and other tools timeout on IPv6-enabled sites (lobste.rs, etc.) while IPv4-only sites (Google, GitHub) work fine.

## Changes

Adds `network.force_ipv4: true` config option that monkey-patches `socket.getaddrinfo` to resolve as `AF_INET` when the caller didn't request a specific address family. Falls back to full resolution if no A record exists, so pure-IPv6 hosts still work.

- **hermes_constants.py** — `apply_ipv4_preference(force)` function (import-safe, no deps)
- **hermes_cli/config.py** — `network.force_ipv4: false` in DEFAULT_CONFIG (no version bump needed — deep merge provides defaults automatically)
- **hermes_cli/main.py** — Applied at module level after dotenv/logging init
- **gateway/run.py** — Applied at module level after config bridging
- **cron/scheduler.py** — Applied in `run_job()` after config load
- **tests/test_ipv4_preference.py** — 7 tests covering patch/noop/double-patch/family passthrough/gaierror fallback

## Usage

```yaml
# config.yaml
network:
  force_ipv4: true
```

## Design

- Default: `false` (no behavior change for existing users)
- Patches `socket.getaddrinfo` at the lowest level, so ALL HTTP paths are covered (httpx, requests, urllib, OpenAI SDK, Firecrawl, etc.)
- Explicit `AF_INET6` requests pass through unmodified
- Pure-IPv6 hosts (no A record) fall back to standard resolution
- Double-patch guard prevents re-wrapping
- Applied early at all three entry points (CLI, gateway, cron) before any HTTP clients are created

## Reported by
User @29n on X — Chinese Ubuntu server with unreachable IPv6.