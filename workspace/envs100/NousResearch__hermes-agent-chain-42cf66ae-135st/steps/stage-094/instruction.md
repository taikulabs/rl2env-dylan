**feat: add native Anthropic auxiliary vision**

## Summary
- add native Anthropic auxiliary client wrappers so auxiliary tasks can use the Anthropic Messages API through the existing chat.completions-style interface
- convert OpenAI-style image_url content into Anthropic native image blocks for auxiliary vision requests
- extend vision backend auto-routing to include Anthropic and prefer the selected main provider when it supports vision
- stop auto-using `~/.claude.json` managed keys for the native Anthropic provider; follow the opencode-style OAuth/setup-token path instead
- keep setup/tool availability aligned with the runtime resolver so Anthropic-backed vision is surfaced correctly

## Root cause investigation
- reproduced the native Anthropic chat failure on the current branch and on a detached origin/main worktree
- confirmed the failure predates phase 2 changes
- isolated it to Claude native managed keys from `~/.claude.json`: direct Anthropic Messages API calls to Sonnet/Opus 4.6 return 500 in this environment, while Haiku works
- verified this is outside Hermes by reproducing it with minimal direct Anthropic SDK calls
- reviewed `~/agent-codebases/opencode` and `~/agent-codebases/clawdbot`; both align around OAuth/setup-token style Anthropic auth rather than treating Claude `/login` managed keys as the canonical direct-native path

## Fix approach
- remove `~/.claude.json primaryApiKey` from native Anthropic credential resolution
- keep Claude Code OAuth/setup-token credentials from `~/.claude/.credentials.json` and explicit `CLAUDE_CODE_OAUTH_TOKEN` / `ANTHROPIC_TOKEN` overrides
- preserve source classification for diagnostics only
- retain native Anthropic auxiliary vision support on the proper OAuth/setup-token path

## Local OAuth/setup-token flow verification
- ran `claude setup-token` locally
- stored the resulting long-lived token into `CLAUDE_CODE_OAUTH_TOKEN` and cleared `ANTHROPIC_TOKEN` / `ANTHROPIC_API_KEY`
- verified native Anthropic chat works locally after that with:
  - `python -m hermes_cli.main chat --provider anthropic -m claude-sonnet-4-6 -t vision,file -Q -q "Just say hello in one sentence."`
- verified end-to-end vision tool execution through native Anthropic with:
  - `python -m hermes_cli.main chat --provider anthropic -m claude-sonnet-4-6 -t vision,file -Q -q "Please use vision_analyze on .../website/build/img/logo.png and briefly tell me what the image shows."`