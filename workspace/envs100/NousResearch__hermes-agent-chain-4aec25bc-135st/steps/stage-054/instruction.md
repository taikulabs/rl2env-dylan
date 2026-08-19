**feat(config): add install-method stamping + Docker detection**

## Summary
- `stamp_install_method()` writes `~/.hermes/.install_method` (creates parent dir if needed)
- `detect_install_method()` reads stamp first, then managed system, container, git, pip
- `recommended_update_command_for_method()` gains Docker guidance
- Dockerfile stamps "docker", install.sh stamps "git", cmd_postinstall stamps "pip"
- (install.ps1 stamping deferred to PR 2 which adds the Windows installer changes)

Tracking: #27826