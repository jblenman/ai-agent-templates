# AI Agent Templates

Configuration templates and starter files for AI coding agents.

## Tools

| Tool | Description |
|------|-------------|
| [Claude Code](claude-code/) | Anthropic's official CLI — workflow, permissions, and memory configuration |
| [Codex CLI](codex/) | OpenAI's terminal coding agent — optimized for Claude Code-like reasoning |
| [OpenCode](opencode/) | Provider-agnostic terminal agent — optimized for Azure AI Foundry / AVD |

## Model Profiles

The default configs target multi-model Azure deployments (gpt-5.2/5.3/5.4). For systems with limited model availability, use a model-specific profile instead:

| Profile | Models | Environment | Location |
|---------|--------|-------------|----------|
| Default | gpt-5.2 / 5.3-codex / 5.4 / 5-mini | AVD (air-gapped) | `opencode/`, `codex/` |
| [GPT-5.1](opencode/profiles/gpt-5.1/) | gpt-5.1 only | Federal (standard) | `*/profiles/gpt-5.1/` |

Profiles include their own config, AGENTS.md (heavier coaching for weaker models), and setup guide. See the SETUP.md in each profile for installation instructions.

---

## Claude Code

Templates for [Claude Code](https://github.com/anthropics/claude-code) — Anthropic's official CLI.

| File | Purpose | Install location |
|------|---------|-----------------|
| [`claude-code/CLAUDE.md`](claude-code/CLAUDE.md) | Global instructions | `~/.claude/CLAUDE.md` |
| [`claude-code/settings.json`](claude-code/settings.json) | Broad permissions (no prompts) | `~/.claude/settings.json` |
| [`claude-code/GUIDE.md`](claude-code/GUIDE.md) | Reference — permissions, memory, hooks, image limits | — |

### Quick install

```bash
mkdir -p ~/.claude
curl -o ~/.claude/CLAUDE.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/claude-code/CLAUDE.md
curl -o ~/.claude/settings.json https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/claude-code/settings.json
```

### Highlights

- Minimal CLAUDE.md — Claude reasons well natively, so coaching focuses on workflow and code quality rather than compensating for reasoning deficiencies
- Broad `settings.json` permissions — no approval prompts for standard operations
- Guide covers: permission patterns, memory system, hooks, image context limits (critical gotcha)

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

### GPT-5.1 Profile

For systems with only gpt-5.1 available. See [`codex/profiles/gpt-5.1/SETUP.md`](codex/profiles/gpt-5.1/SETUP.md) for full instructions.

Key differences from default:
- Model set to `gpt-5.1`, `review_model` also `gpt-5.1` (no fallback)
- `web_search = "cached"` enabled — routed through Azure API; 5.1 benefits from lookup ability
- `tool_output_token_limit = 25000` — conservative for 128k context window
- AGENTS.md has heavier coaching: explicit reasoning requirements, common failure modes, security practices for federal systems

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
- Developer-instinct git safety rules (treat dotfolders like `.vs/`)
- Session management strategy for OpenCode's compaction behavior

### GPT-5.1 Profile

For systems with only gpt-5.1 available. See [`opencode/profiles/gpt-5.1/SETUP.md`](opencode/profiles/gpt-5.1/SETUP.md) for full instructions.

Key differences from default:
- Single model (`gpt-5.1`), no `small_model`
- LSP downloads from GitHub allowed (well-known source; helps compensate for 5.1's weaker understanding)
- Compaction reserve bumped from 10000 to 15000 (smaller context window needs more buffer)
- AGENTS.md has heavier coaching: explicit reasoning requirements, common failure modes, mandatory plan-first workflow, security practices for federal systems
- Agent team uses shared files but models need updating to `gpt-5.1` (setup guide includes a one-liner)

---

## Sharing instructions across tools

All three tools can share a single `CLAUDE.md` instruction file:

- **Claude Code** — reads `CLAUDE.md` natively (global: `~/.claude/CLAUDE.md`, project: `.claude/CLAUDE.md`)
- **OpenCode** — reads `CLAUDE.md` at the project level natively. For global, add `"instructions": ["~\\.claude\\CLAUDE.md"]` to `opencode.json`
- **Codex CLI** — add to `~/.codex/config.toml`:
  ```toml
  project_doc_fallback_filenames = [".claude/CLAUDE.md", "CLAUDE.md"]
  ```

OpenCode-specific features (agents, commands, skills) stay in `~/.config/opencode/` — Claude Code and Codex don't have equivalents for these.

---

## Per-project setup

Add a project-level instruction file at the repo root for project-specific context:

- Claude Code: `.claude/CLAUDE.md`
- OpenCode: `AGENTS.md` or `CLAUDE.md` (reads both natively)
- Codex: `AGENTS.md` or `.claude/CLAUDE.md` (with `project_doc_fallback_filenames`)

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
