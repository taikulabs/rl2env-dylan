**fix(security): restrict dashboard plugin backend auto-import to bundled plugins — defense-in-depth**

## Summary

Addresses #43719 (dashboard plugin RCE) as **defense-in-depth** for the plugin
auto-import path.

The web server auto-imports and mounts the Python backend
(`dashboard/manifest.json` → `api` file) of plugins found in **user**
(`~/.hermes/plugins/`) and **project** (`./.hermes/plugins/`) dirs, not just
bundled plugins (verified on current `main` `b4cb33cd4`: `_mount_plugin_api_routes`
restricts import to `bundled` **and `user`**; only `project` is refused). So any
plugin that reaches `~/.hermes/plugins/` gets arbitrary Python executed on the
next dashboard start.

## ⚠️ Threat-model note (scope corrected from the original issue)

#43719's **originally-documented delivery chain** — a public `--insecure`
dashboard + an open/unauthenticated API used to `git clone` a malicious repo
into `~/.hermes/plugins/` — **is already mitigated on `main`.** Since the June
2026 hermes-0day hardening, a non-loopback dashboard bind **always requires an
auth provider** and `--insecure` no longer bypasses the auth gate
(`hermes_cli/web_server.py` ~12830, `main.py` ~11029). There is no longer an
unauthenticated public dashboard for an attacker to drive that chain through.

This PR therefore **does not** claim to close that (now-authenticated) network
path. It removes the **residual** hazard — *arbitrary code executes merely
because a plugin is present on disk* — which still applies when a plugin arrives
by other means:
- a socially-engineered `git clone` ("install this useful Hermes plugin"),
- a supply-chain drop / compromised dependency,
- an authenticated-but-malicious actor, or
- a future regression in the dashboard auth gate.

Untrusted on-disk code should not auto-execute. This is the same principle as
the prior GHSA-5qr3-c538-wm9j / #29156 hardening, tightened from "bundled+user"
to **bundled-only**.

> Given the auth-gate mitigation, the maintainer may wish to re-triage #43719's
> P1 severity — the active unauthenticated-RCE is gone; this is hardening. Flagging
> rather than deciding.

## Fix

Restrict dashboard backend Python auto-import to **bundled plugins only**. User
and project plugins may still extend the dashboard UI via static JS/CSS, but
their `api` Python file is never auto-imported. Two layers:
- `_discover_dashboard_plugins`: scrub `api`/`_api_file` for `user`/`project`
  sources; scan bundled-first so bundled wins name conflicts (a non-bundled
  plugin can't shadow a trusted backend route);
- `_mount_plugin_api_routes`: re-refuse `user`/`project` backend import at mount.

The single backend `exec_module` site is `_mount_plugin_api_routes`; both layers
gate it. Static-asset serving stays allowed (suffix allowlist; `.py` → 404).

## Salvage / attribution

Salvaged from **#44472** (@egilewski), cherry-picked onto current `main`;
authored by @egilewski. Supersedes (crediting-redirect close on merge):
- **#43786** (@egilewski) — same author's earlier, broader attempt; #44472 is the refined replacement.
- **#43794** (@maxpetrusenkoagent) — narrower (blocks installs, not already-dropped-plugin import).

## Tests

`tests/hermes_cli/test_project_plugin_rce_bypass.py` (39) pass; the import-
suppression contract asserts `spec_from_file_location.call_count == 0` for
user/project and is mutation-checked (removing the user-source guard fails
`test_user_source_api_is_not_imported`). Source is not spoofable (set from the
trusted `search_dirs` constant, never read from the manifest); name-collision
shadowing is closed (bundled-first dedup). (3 unrelated `TestPtyWebSocket`
failures are a pre-existing macOS pty test-env artifact, identical on bare `main`.)