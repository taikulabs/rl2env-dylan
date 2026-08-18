**fix(gateway): include resolved node path in systemd unit**

## Summary
- include the directory of the resolved `node` binary when generating the gateway systemd unit PATH
- keep the existing venv and `node_modules/.bin` entries unchanged
- add a regression test covering Node installed under `~/.nvm/.../bin`

## Problem
On Linux, if Node is installed via `nvm`, `hermes gateway install` can generate a systemd unit whose PATH omits the actual Node binary directory. When WhatsApp is enabled, the gateway service then fails the WhatsApp bridge requirement check and can enter a restart loop.

## Reproduction
This was reproduced on a fresh Ubuntu 24.04 install with upstream `main`, Node installed only through `nvm`, and:
```bash
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot
```
Then:
```bash
hermes gateway install
systemctl --user restart hermes-gateway
```
The generated unit PATH omitted `~/.nvm/.../bin`, `node` was missing under the service environment, and the gateway crash-looped.

## Fix
When generating the systemd unit, resolve `node` from the current install environment and append its parent directory to the service PATH if present.