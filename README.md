# AI Agent Templates

Configuration templates and starter files for AI coding agents.

## Tools

| Tool | Description |
|------|-------------|
| [Claude Code](claude-code/) | Anthropic's official CLI — workflow, permissions, and memory configuration |
| [Codex CLI](codex/) | OpenAI's terminal coding agent — optimized for Claude Code-like reasoning |
| [OpenCode](opencode/) | Provider-agnostic terminal agent — optimized for Azure AI Foundry / AVD |

## Model Profiles

The default configs target multi-model Azure deployments with a Sol-tier model (GPT-6.1 Sol on OpenAI; your Sol-tier deployment on Azure) as the daily driver. For systems with limited model availability, use a model-specific profile instead:

| Profile | Models | Environment | Location |
|---------|--------|-------------|----------|
| **Default** | **Sol tier** (gpt-6.1-sol / your Azure deployment) + a Luna-tier small model | AVD (air-gapped) | `opencode/`, `codex/` |
| [Thorough](opencode/profiles/thorough/) | the default model at `reasoning_effort = "high"` | Same as default; opt-in for depth-over-speed | `opencode/profiles/thorough/` |
| [GPT-5.1](opencode/profiles/gpt-5.1/) | gpt-5.1 only | Federal (standard) | `*/profiles/gpt-5.1/` |
| [Bedrock / restricted gov](claude-code/profiles/bedrock-gov/) | Claude Opus 5 via Amazon Bedrock | Isolated government dev environment (no internet, hard data boundary) | `claude-code/profiles/bedrock-gov/` |

**Why the defaults stay short:** OpenAI's guidance for GPT-5.6 and GPT-6 is leaner prompts (higher evals, far fewer tokens), autonomy boundaries stated once, and no "think harder" coaching; the newest models follow AGENTS.md and skills closely and pause on contradictions. The Oct 2026 additions (evidence rules, session notes, knowledge base, skills) are behaviour the models do not have by default — see each tool's guide.

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
- Oct 2026: Evidence rules for tool results, session notes enforced by the `session-guard` plugin from [claude-code-kit](https://github.com/jblenman/claude-code-kit), the shared skills and the knowledge-base starter; `cleanupPeriodDays = 90` so transcripts outlive the default 30 days

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
| [`codex/config.toml`](codex/config.toml) | Global config (Codex 0.160 keys) | `~/.codex/config.toml` |
| [`codex/AGENTS.md`](codex/AGENTS.md) | Global coaching instructions | `~/.codex/AGENTS.md` |
| [`codex/hooks.json`](codex/hooks.json) + [`codex/hooks/session_notes.py`](codex/hooks/session_notes.py) | Session-notes hooks (SessionStart / Stop / PreCompact) | `~/.codex/hooks.json`, `~/.codex/hooks/` |
| [`codex/profiles/*.config.toml`](codex/profiles/) | Profile overlays `deep`, `fast`, `luna` (`codex --profile <name>`) | `~/.codex/<name>.config.toml` |
| [`skills/`](skills/) | `azure-cli`, `session-notes`, `kb-capture` — referenced in place by `[[skills.config]]` | the clone |
| [`knowledge-base/`](knowledge-base/README.md) | A starter knowledge base the agent reads first and gives back to | `~/knowledge-base/` (or a team repo) |
| [`codex/GUIDE.md`](codex/GUIDE.md) | Reference — what each setting does and why | — |

### Quick install

```bash
git clone https://github.com/jblenman/ai-agent-templates ~/ai-agent-templates
mkdir -p ~/.codex/hooks
cp ~/ai-agent-templates/codex/config.toml ~/ai-agent-templates/codex/AGENTS.md ~/ai-agent-templates/codex/hooks.json ~/.codex/
cp ~/ai-agent-templates/codex/hooks/session_notes.py ~/.codex/hooks/
cp ~/ai-agent-templates/codex/profiles/*.config.toml ~/.codex/
```

Then `/hooks` once inside Codex to trust the session-notes hooks. The skills are read from the clone (`[[skills.config]]` paths in `config.toml`).

### Highlights

- **Evidence Rules** in AGENTS.md — an empty tool result is not "no access": bisect the command, read exit code and stderr, quote the command and output for every claim about the environment, three different attempts before a hand-back. Written after a Luna-tier model turned a malformed `az --query` into "your account has no access".
- **Session notes** a new session boots from, enforced by hooks: `SessionStart` hands the file to the model, `Stop` continues the turn once while it is stale or missing, `PreCompact` records compactions.
- **Skills**: `azure-cli` (login and scope first, inventory without filters, JMESPath rules), `session-notes`, `kb-capture`; **knowledge-base** starter with read-first and give-back rules.
- `model = "gpt-6.1-sol"` (Codex's default); OpenAI's 2026 tiers explained in the guide — Sol (capable) / Terra / Luna (efficient, nano-class). A `luna` profile for environments that only have `gpt-5.6-luna`.
- `approval_policy = "on-request"` — `untrusted` is no longer supported by Codex.
- Profiles are overlay files (`deep`, `fast`, `luna`), not `[profiles.*]` tables (retired in 0.134).
- `tool_output_token_limit = 32000`, `memories`, `undo`, `request_permissions`, hooks enabled; analytics, feedback and update checks off; full local history.

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
- `azure/gpt-6.1-sol` as the daily driver (Sol tier), `azure/gpt-5.6-luna` as `small_model` and for the cheap agents; model limits from models.dev (1.05M context / 128K output)
- Per-model `options.reasoningEffort = "medium"` (`high` for the Luna tier) and `options.textVerbosity = "low"`
- **Evidence Rules**, Session Notes, Knowledge Base and Skills sections in AGENTS.md (same as the Codex template); the `session-notes.js` plugin enforces the notes file the way a Stop hook does elsewhere
- Shared skills read in place via `skills.paths`; AGENTS.md keeps the modular outcome-first structure (Role / Goal / Success / Constraints / Output / Evidence / Stop Rules)
- Developer-instinct git safety rules (treat dotfolders like `.vs/`)
- Compaction setting uses the new `preserve_recent_tokens` key (renamed from `reserved` in OpenCode v1.14.19)

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

OpenCode-specific agents and commands stay in `~/.config/opencode/`. Skills are shared: the folders under [`skills/`](skills/) load in Codex (`[[skills.config]]`), OpenCode (`~/.config/opencode/skills/` or `.opencode/skills/`) and Claude Code (`~/.claude/skills/`) alike, and the [`knowledge-base/`](knowledge-base/README.md) starter is read by all three.

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
