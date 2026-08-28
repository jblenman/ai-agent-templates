# AI Agent Templates

Configuration templates and starter files for AI coding agents.

## Tools

| Tool | Description |
|------|-------------|
| [Claude Code](claude-code/) | Anthropic's official CLI — workflow, permissions, and memory configuration |
| [Codex CLI](codex/) | OpenAI's terminal coding agent — optimized for Claude Code-like reasoning |
| [OpenCode](opencode/) | Provider-agnostic terminal agent — optimized for Azure AI Foundry / AVD |

## Model Profiles

The default configs target multi-model Azure deployments with GPT-5.5 as the daily driver. For systems with limited model availability, use a model-specific profile instead:

| Profile | Models | Environment | Location |
|---------|--------|-------------|----------|
| **Default** | **gpt-5.5 / 5-mini** (+ 5.4, 5.3-codex fallbacks) | AVD (air-gapped) | `opencode/`, `codex/` |
| [Thorough](opencode/profiles/thorough/) | gpt-5.5 at `reasoning_effort = "high"` | Same as default; opt-in for depth-over-speed | `opencode/profiles/thorough/` |
| [GPT-5.1](opencode/profiles/gpt-5.1/) | gpt-5.1 only | Federal (standard) | `*/profiles/gpt-5.1/` |
| [Bedrock / restricted gov](claude-code/profiles/bedrock-gov/) | Claude Opus 5 via Amazon Bedrock | Isolated government dev environment (no internet, hard data boundary) | `claude-code/profiles/bedrock-gov/` |

**Why the default targets GPT-5.5:** OpenAI's prompt guidance for 5.5 inverts the playbook from earlier models — short, outcome-first AGENTS.md beats process-heavy "think step-by-step / consider alternatives" coaching, which now causes 5.5 to over-process and stop early during rollouts. The default templates use the modular Role / Goal / Success / Constraints / Output / Stop Rules structure OpenAI recommends. The GPT-5.1 profile keeps the heavier coaching for weaker models.

**The Thorough profile** is for users who want depth-over-speed on the same model. It pairs the outcome-first structure (which 5.5 responds to) with explicit Investigation Requirements that force the agent to read callers, check tests, and surface cross-file impact before implementing. Use it for unfamiliar code, public-interface changes, or design-affecting work; stick with the default for routine work where per-turn latency matters more. Codex CLI users get the equivalent via `codex --profile deep`.

Profiles include their own config, AGENTS.md, and setup guide. See SETUP.md in each profile for installation instructions.

---

## Claude Code

Templates for [Claude Code](https://github.com/anthropics/claude-code) — Anthropic's official CLI.

| File | Purpose | Install location |
|------|---------|-----------------|
| [`claude-code/CLAUDE.md`](claude-code/CLAUDE.md) | Global instructions (Opus 5-tuned) | `~/.claude/CLAUDE.md` |
| [`claude-code/settings.json`](claude-code/settings.json) | Auto mode + read-only allow list | `~/.claude/settings.json` |
| [`claude-code/GUIDE.md`](claude-code/GUIDE.md) | Reference — permissions, settings, memory, hooks, image limits | — |
| [`claude-code/profiles/bedrock-gov/`](claude-code/profiles/bedrock-gov/) | Bedrock / restricted-government profile (CLAUDE.md, settings.json, SETUP.md) | see its SETUP.md |

### Quick install

```powershell
$src = "$HOME\ai-agent-templates\claude-code"   # clone of this repo (private — raw URLs need a token)
New-Item -ItemType Directory -Path "$HOME\.claude" -Force
Copy-Item "$src\CLAUDE.md"     "$HOME\.claude\CLAUDE.md"
Copy-Item "$src\settings.json" "$HOME\.claude\settings.json"
```

### Highlights

- CLAUDE.md written for Opus 5-class models: goals and constraints, no step choreography (current models over-plan when told to plan), explicit conciseness and scope discipline
- Accuracy habits baked in: verified-vs-recalled, hard identifiers before acting on a guess, evidence-backed reports, plain register, incremental "top N" searches
- `settings.json` = `defaultMode: "auto"` with only never-lossy tools pre-approved — read anything without prompts, classifier reviews edits and commands, destructive actions still confirm. No `Bash(*)` blanket allow.
- Guide covers: permission model and why, settings keys, memory system, hook safety (`|| exit 1`), image context limits (critical gotcha)

### Bedrock / restricted-government profile

For an isolated government dev environment where Claude is reached only through Amazon Bedrock. See [`claude-code/profiles/bedrock-gov/SETUP.md`](claude-code/profiles/bedrock-gov/SETUP.md).

Key differences from default:
- `CLAUDE_CODE_USE_BEDROCK=1`; `opus` alias pinned to `us.anthropic.claude-opus-5[1m]` (`us-gov.` prefix in GovCloud); 1M context
- `WebFetch` and `WebSearch` **denied** — WebSearch doesn't exist on Bedrock, and WebFetch would send each hostname to `api.anthropic.com` before fetching
- Telemetry, error reporting, feature-flag fetches, `/feedback` `/bug` `/share`, and auto-update all off; Remote Control explicitly off; session URLs dropped from commit trailers
- Auto mode with only `Read`/`Glob`/`Grep` pre-approved (Sonnet 5 must be enabled in the account — it runs the classifier; otherwise sessions start in Manual)
- CLAUDE.md gains an "Environment — read first" section: nothing internal leaves the boundary, sanitize anything that will, work as if offline, no installs without approval, minimal hand-transferable diffs

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

- `model = "gpt-5.5"` with `model_reasoning_effort = "medium"` and `model_verbosity = "low"` — matches OpenAI's official guidance for 5.5
- `model_auto_compact_token_limit = 270000` — caps just under the 272K input pricing cliff (where requests get billed at 2× input / 1.5× output)
- `tool_output_token_limit = 32000` — reads large files without truncation
- `child_agents_md = true` — sub-agents inherit your coaching (off by default)
- `memories = true` — cross-session memory across restarts
- `undo = true` — git snapshot before each change, per-step rollback
- `[profiles.deep]` raises reasoning to `high` on the same model for hard design/audit work
- TUI hotkeys (Codex v0.124.0+): `Alt+,` lower / `Alt+.` raise reasoning live
- Analytics, feedback, and update checks disabled
- Full local history saved

### GPT-5.1 Profile

For systems with only gpt-5.1 available. See [`codex/profiles/gpt-5.1/SETUP.md`](codex/profiles/gpt-5.1/SETUP.md) for full instructions.

Key differences from default:
- Model set to `gpt-5.1`, `review_model` also `gpt-5.1` (no fallback)
- `model_reasoning_effort = "xhigh"` retained — older models still benefit from heavy reasoning escalation
- `web_search = "cached"` enabled — routed through Azure API; 5.1 benefits from lookup ability
- `tool_output_token_limit = 25000` — conservative for 128k context window
- AGENTS.md keeps the heavier "think step-by-step / consider alternatives / mandatory plan-first" coaching that 5.1 still benefits from. **Don't copy this coaching back to the GPT-5.5 default** — it now hurts on 5.5.

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
- `gpt-5.5` as primary across all agents, `gpt-5-mini` as small_model fallback for background tasks
- Per-model `options.reasoningEffort = "medium"` and `options.textVerbosity = "low"` for 5.5
- Context limits capped at 272,000 (under OpenAI's 2× pricing cliff for prompts above that threshold)
- AGENTS.md uses the modular outcome-first structure OpenAI recommends for 5.5 (Role / Goal / Success / Constraints / Output / Stop Rules) — no "think step-by-step" coaching that causes 5.5 to over-process
- Developer-instinct git safety rules (treat dotfolders like `.vs/`)
- Compaction setting uses the new `preserve_recent_tokens` key (renamed from `reserved` in OpenCode v1.14.19)
- **Requires OpenCode v1.14.25+** for correct GPT-5.5 OAuth context limits — older versions cap at 256K and the model self-reports `262144`

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
