# AI Agent Templates

Configuration templates and starter files for AI coding agents.

## Codex CLI

Templates for [OpenAI Codex CLI](https://github.com/openai/codex) — optimized for Claude Code-like reasoning, maximum local context, and minimal outbound data.

| File | Purpose | Install |
|------|---------|---------|
| [`codex/config.toml`](codex/config.toml) | Global config | `~/.codex/config.toml` |
| [`codex/AGENTS.md`](codex/AGENTS.md) | Global coaching instructions | `~/.codex/AGENTS.md` |

### What these do

**config.toml**
- `model_reasoning_effort = "xhigh"` — pushes GPT to explore alternatives and self-review before answering
- `tool_output_token_limit = 32000` — lets it read large files and command output without truncation
- `child_agents_md = true` — sub-agents inherit your coaching instructions (off by default)
- `memories = true` — cross-session memory that persists across restarts
- `undo = true` — git snapshot before each change, enabling per-step rollback
- Analytics, feedback, and update checks disabled
- Full local history saved

**AGENTS.md**
- Coaching for step-by-step reasoning and exploring alternatives before acting
- Explore-then-implement workflow (read before changing)
- Strict git safety rules (learned the hard way — GPT will literally force-push `.gitignore`d files if you ask it to "commit everything")
- Direct communication style with minimal unnecessary check-ins

### Quick install

```bash
mkdir -p ~/.codex
curl -o ~/.codex/config.toml https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/codex/config.toml
curl -o ~/.codex/AGENTS.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/codex/AGENTS.md
```

### Reusing Claude Code instructions

If you already use Claude Code, you can share instructions across both tools. Add to `config.toml`:

```toml
project_doc_fallback_filenames = [".claude/CLAUDE.md", "CLAUDE.md"]
```

Codex will pick up `.claude/CLAUDE.md` when no `AGENTS.md` exists in a project.

### Per-project AGENTS.md

Add a project-level `AGENTS.md` or `.claude/CLAUDE.md` at the repo root with project-specific context:

```markdown
## Project Context
Brief description of what this project does.

## Tech Stack
Languages, frameworks, key dependencies.

## Coding Conventions
Style rules, naming conventions, patterns to follow or avoid.

## Commands
- Build: `...`
- Test: `...`
- Lint: `...`
```

---

More templates coming as things get tested and validated.
