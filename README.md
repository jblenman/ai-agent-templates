# AI Agent Templates

Configuration templates and starter files for AI coding agents.

## Tools

| Tool | Description |
|------|-------------|
| [Codex CLI](codex/) | OpenAI's terminal coding agent — optimized for Claude Code-like reasoning |
| [OpenCode](opencode/) | Provider-agnostic terminal agent — optimized for Azure AI Foundry / AVD |

---

## Codex CLI

Templates for [OpenAI Codex CLI](https://github.com/openai/codex).

| File | Purpose | Install location |
|------|---------|-----------------|
| [`codex/config.toml`](codex/config.toml) | Global config | `~/.codex/config.toml` |
| [`codex/AGENTS.md`](codex/AGENTS.md) | Global coaching instructions | `~/.codex/AGENTS.md` |
| [`codex/GUIDE.md`](codex/GUIDE.md) | Reference — what each setting does and why | — |

### Quick install

```bash
mkdir -p ~/.codex
curl -o ~/.codex/config.toml https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/codex/config.toml
curl -o ~/.codex/AGENTS.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/codex/AGENTS.md
```

### Highlights

- `model_reasoning_effort = "xhigh"` — pushes GPT to explore alternatives and self-review before answering
- `tool_output_token_limit = 32000` — reads large files without truncation
- `child_agents_md = true` — sub-agents inherit your coaching (off by default)
- `memories = true` — cross-session memory across restarts
- `undo = true` — git snapshot before each change, per-step rollback
- Analytics, feedback, and update checks disabled
- Full local history saved

---

## OpenCode

Templates for [OpenCode](https://github.com/sst/opencode) — specifically for Azure AI Foundry / AVD deployments.

| File | Purpose | Install location |
|------|---------|-----------------|
| [`opencode/opencode.json`](opencode/opencode.json) | Provider and model config | `~/.config/opencode/opencode.json` |
| [`opencode/AGENTS.md`](opencode/AGENTS.md) | Global coaching instructions | `~/.config/opencode/AGENTS.md` |
| [`opencode/GUIDE.md`](opencode/GUIDE.md) | Reference — what each setting does and why | — |

### Quick install

```bash
mkdir -p ~/.config/opencode
curl -o ~/.config/opencode/opencode.json https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/opencode/opencode.json
curl -o ~/.config/opencode/AGENTS.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/opencode/AGENTS.md
# Edit opencode.json — replace YOUR_RESOURCE_NAME with your Azure resource name
```

Set required env vars to block unnecessary outbound calls (Windows):

```powershell
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_SHARE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_MODELS_FETCH", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_AUTOUPDATE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_LSP_DOWNLOAD", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_EXTERNAL_SKILLS", "true", "User")
```

### Highlights

- Uses `@ai-sdk/azure` (not `openai-compatible`) — avoids the Azure URL path bug
- `gpt-5.2` as primary, `gpt-5-mini` as fast fallback
- Coaching for step-by-step reasoning and exploring alternatives
- Strict git safety rules
- Session management strategy for OpenCode's context truncation problem

---

## Sharing instructions across tools

If you use both Codex CLI and Claude Code on the same projects, you can share a single instruction file. Add to `~/.codex/config.toml`:

```toml
project_doc_fallback_filenames = [".claude/CLAUDE.md", "CLAUDE.md"]
```

Codex will pick up `.claude/CLAUDE.md` when no `AGENTS.md` exists in a project.

---

## Per-project setup

Add a project-level instruction file at the repo root for project-specific context:

- Codex: `AGENTS.md` or `.claude/CLAUDE.md`
- OpenCode: `AGENTS.md`
- Claude Code: `.claude/CLAUDE.md`

```markdown
## Project Context
[What this project is and does]

## Tech Stack
[Languages, frameworks, key dependencies]

## Coding Conventions
[Style rules, naming conventions, patterns to follow or avoid]

## Commands
- Build: `...`
- Test: `...`
- Lint: `...`
```
