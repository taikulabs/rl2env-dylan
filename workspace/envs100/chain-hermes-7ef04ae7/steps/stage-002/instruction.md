**fix(gateway): gate quick_commands through slash access policy**

## Summary
Config-backed `quick_commands` are now gated through the gateway's admin/user slash-access policy, closing an authorization bypass: a non-admin allowlisted gateway user could invoke admin-only quick commands — including `type: exec` shell commands that run in the gateway process — even when the operator set `allow_admin_from` / `user_allowed_commands` to lock them out.

Root cause: the early slash gate in `_handle_message` only fires for registry-known commands (`is_gateway_known_command(canonical)`). `quick_commands` are never in the gateway command registry, so they slipped straight past the gate to the `type: exec` dispatch sink unchecked.

.

## Changes
- `gateway/run.py`: call `_check_slash_access(source, command)` at the `quick_commands` dispatch site (the single exec chokepoint, cold-path only), using the raw typed command name, before resolving/running `qcmd`.
- `tests/gateway/test_slash_access_dispatch.py`: 3 integration tests driving the real `_handle_message` — non-admin denied for an unlisted exec quick command (the PoC), admin runs it, non-admin runs it when it's in `user_allowed_commands`.

## Validation
Targeted suite: `tests/gateway/test_slash_access_dispatch.py` — 21/21 passing.

E2E against the real `GatewayRunner._handle_message`:

| Case | Result |
|---|---|
| Non-admin (999), empty `user_allowed_commands` (the PoC) | ⛔ DENIED — bypass closed |
| Admin (111) | RUNS — admin unaffected |
| Non-admin (999), command in `user_allowed_commands` | RUNS — opt-in works |
| No policy set (`allow_admin_from` unset) | RUNS — backward-compat intact |

## Credit
Same fix independently submitted in #44791 (@maxpetrusenko, earliest) and #45536 (@zapabob). This salvage uses the sink-gate approach; both contributors co-authored.

## Infographic

![quick-command-auth-bypass-sealed](https://v3b.fal.media/files/b/0aa01728/9m8RXEaVWaxjUEseH8Tje_EgsEypvf.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_slash_access_dispatch.py`