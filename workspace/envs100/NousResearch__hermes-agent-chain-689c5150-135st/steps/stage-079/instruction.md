**security: comprehensive supply chain hardening**

## Summary

Supply chain hardening — pins all mutable references to immutable SHAs, tightens CI permissions, and fixes a few code-level security bugs. No behavior changes for users.

## Changes

### CI/CD Hardening (8 workflow files)
- **Pin all 12 GitHub Actions to full commit SHAs** — mutable `@vN` tags can be silently retargeted if a maintainer account is compromised
- **Add `permissions: {contents: read}`** to 4 workflows that had no explicit permissions (tests, contributor-check, docs-site-checks, nix)
- **Pin CI pip installs** to exact versions (`pyyaml==6.0.2`, `httpx==0.28.1`) in deploy-site and skills-index workflows
- **Extend supply-chain-audit.yml** with 4 new scanners: workflow file changes, Dockerfile changes, dependency manifest changes, and unpinned Actions version tags

### Dependency Pinning
- Pin `atroposlib`, `tinker`, `yc-bench` git deps to commit SHAs in pyproject.toml
- Pin WhatsApp Baileys from mutable branch name to commit SHA

### Code Fixes (4 Python files)
- **Tool registry** (`tools/registry.py`): Reject cross-family tool name shadowing — plugins/MCP can no longer silently overwrite built-in tools like `terminal` or `write_file`. MCP-to-MCP overwrites still allowed (server refresh). Was: log warning, overwrite anyway.
- **MCP description scanning** (`tools/mcp_tool.py`): Scan MCP tool descriptions for 10 prompt injection patterns (role overrides, system prompt injection, concealment instructions, etc.) and log warnings
- **MCP refresh notification** (`tools/mcp_tool.py`): Log added/removed tools at WARNING level when servers dynamically change their tool list
- **Skill manager** (`tools/skill_manager_tool.py`): Fix bug where agent-created skills with `dangerous` security findings were silently allowed (`ask→None→allow` code path)

## Test Results
- 247 targeted tests pass (registry, MCP, skill manager)
- Updated `test_mcp_tool.py`: collision test expects rejection; MCP-to-MCP overwrite still works