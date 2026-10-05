# OpenCode — Configuration Guide

Reference for `opencode.json`, `AGENTS.md`, agent team, skills, commands, and tools. Includes reasoning behind each choice and alternatives.

## Quick Install

Clone the templates repo, then copy files into place. Direct downloads from `raw.githubusercontent.com` may be blocked by content filters on restricted networks, but `git clone` works.

```powershell
# === Clone the templates repo (if not already cloned) ===
git clone https://github.com/jblenman/ai-agent-templates.git "$HOME\ai-agent-templates"
# Or if already cloned:
# cd "$HOME\ai-agent-templates" && git pull

# === Copy everything into place ===
$src = "$HOME\ai-agent-templates\opencode"
$dst = "$HOME\.config\opencode"

# Config + coaching
mkdir -Force $dst
Copy-Item "$src\opencode.json" "$dst\opencode.json"
Copy-Item "$src\AGENTS.md" "$dst\AGENTS.md"
# Edit opencode.json — replace YOUR_RESOURCE_NAME with your Azure resource name

# Agent team
mkdir -Force "$dst\agents"
Copy-Item "$src\agents\*.md" "$dst\agents\"

# Skills — the OpenCode-only one is copied; the shared ones (azure-cli, session-notes, kb-capture)
# are read in place from the clone through "skills": { "paths": [...] } in opencode.json
mkdir -Force "$dst\skills\azure-devops-api"
Copy-Item "$src\skills\azure-devops-api\SKILL.md" "$dst\skills\azure-devops-api\SKILL.md"

# Session-notes plugin (local JS plugin, auto-loaded from this folder)
mkdir -Force "$dst\plugins"
Copy-Item "$src\plugins\session-notes.js" "$dst\plugins\session-notes.js"

# Commands
mkdir -Force "$dst\commands"
Copy-Item "$src\commands\*.md" "$dst\commands\"
```

### Updating

When templates are updated, pull and re-copy:

```powershell
cd "$HOME\ai-agent-templates"
git pull
$src = "$HOME\ai-agent-templates\opencode"
$dst = "$HOME\.config\opencode"
Copy-Item "$src\opencode.json" "$dst\opencode.json"
Copy-Item "$src\AGENTS.md" "$dst\AGENTS.md"
Copy-Item "$src\agents\*.md" "$dst\agents\"
Copy-Item "$src\skills\azure-devops-api\SKILL.md" "$dst\skills\azure-devops-api\SKILL.md"
Copy-Item "$src\commands\*.md" "$dst\commands\"
```

### Required Environment Variables (Windows AVD)

Set as User environment variables. Restart your terminal after setting these.

```powershell
# Block unnecessary outbound calls
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_SHARE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_MODELS_FETCH", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_AUTOUPDATE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_LSP_DOWNLOAD", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_EXTERNAL_SKILLS", "true", "User")

# Azure OpenAI
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "your-key", "User")

# Azure DevOps (for /workitems and devops agent)
[Environment]::SetEnvironmentVariable("AZURE_DEVOPS_PAT", "your-pat-token", "User")
[Environment]::SetEnvironmentVariable("AZURE_DEVOPS_ORG", "your-org-name", "User")
[Environment]::SetEnvironmentVariable("AZURE_DEVOPS_PROJECT", "your-project-name", "User")

# Critical: OpenCode TUI uses a local HTTP server — must bypass proxy
[Environment]::SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1", "User")

# If your org uses a proxy
# [Environment]::SetEnvironmentVariable("HTTPS_PROXY", "http://proxy:8080", "User")

# If your org has custom CA certificates
# [Environment]::SetEnvironmentVariable("NODE_EXTRA_CA_CERTS", "C:\path\to\ca-bundle.pem", "User")
```

### Windows Terminal: Fix Shift+Enter

Add to your Windows Terminal `settings.json` (Settings > Open JSON file) under `"actions"`:

```json
{
    "command": { "action": "sendInput", "input": "\u001b[13;2u" },
    "id": "User.sendInput.ShiftEnterCustom"
}
```

Without this, Shift+Enter won't create new lines in the OpenCode input.

---

## Agent Team

The agent team gives you specialized subagents that the primary build agent (or you) can invoke via `@mention` or through custom commands.

### Team Roster

| Agent | Role | Model | Tool Access |
|-------|------|-------|-------------|
| **build** (built-in) | Primary coding agent | gpt-5.5 | Full |
| **plan** (built-in) | Read-only exploration (Tab to switch) | gpt-5.5 | Read only |
| **code-reviewer** | Reviews code for quality and security | gpt-5.5 | Read only |
| **qa-tester** | Writes and runs tests | gpt-5.5 | Read + write + bash (test commands allowed) |
| **scribe** | Writes documentation | gpt-5-mini | Read + write (no bash) |
| **researcher** | Explores codebase, gathers context | gpt-5-mini | Read only |
| **security-auditor** | OWASP top 10, vulnerability scanning | gpt-5.5 | Read only |
| **architect** | Design decisions, trade-off analysis | gpt-5.5 | Read only |
| **devops** | Azure DevOps work items, pipelines | gpt-5.5 | Read + write + bash (API calls allowed) |

### Model Assignments Rationale

- **gpt-5.5** for everything except text-heavy / reasoning-light work — better agentic execution and shorter prompts than 5.4 needed less scaffolding. Each agent's specialized behavior comes from its system prompt (architect compares options, security-auditor runs OWASP checks), not from a different base model
- **gpt-5-mini** for text-heavy, reasoning-light work (docs, codebase exploration)
- If a "Pro" tier (e.g., gpt-5.5-pro) is deployed in your Azure Foundry, swap architect / security-auditor to it — Pro mainly buys a deeper reasoning budget on hard, infrequent tasks. Without it, you get most of the same benefit by raising `reasoningEffort` to `"high"` on those two agents

### How to Use

**Direct invocation via @mention:**
```
@code-reviewer review the auth middleware in src/auth/
@security-auditor scan the API controllers
@devops get my active bugs
@architect evaluate whether we should switch from REST to gRPC
```

**Via custom commands (slash commands):**
```
/workitems                           # get your active work items
/workitems bugs assigned to me       # specific query
/review                              # review uncommitted changes
/review src/auth/                    # review specific files
/test src/services/user.ts           # write tests for specific code
/document                            # document recent changes
/security-scan                       # audit changed files
/design migration to microservices   # architecture analysis
```

**Automatic delegation:**
The build agent can invoke subagents when it recognizes a task matches their specialty. For example, after implementing a feature, it may invoke the qa-tester to write tests.

**Navigate child sessions:**
When a subagent runs, it creates a child session. Navigate with:
- `<leader>+Down` — enter child session
- `Right/Left` — cycle between child sessions
- `Up` — return to parent

### Customizing Agents

Agent files are in `~/.config/opencode/agents/`. Edit any `.md` file to change:
- **Model** — change the `model:` frontmatter
- **Prompt** — edit the markdown body
- **Tool access** — toggle tools in the `tools:` frontmatter
- **Permissions** — adjust `permission:` for granular control

Create new agents by adding a new `.md` file. The filename becomes the agent ID.

---

## Azure DevOps Integration

The DevOps agent + skill solve the problem of GPT having to rediscover the REST API every session.

### Why REST instead of CLI

The `az devops` CLI doesn't work reliably on AVD (auth issues, module loading failures). The REST API via PowerShell's `Invoke-RestMethod` is reliable and requires only a PAT token.

### Setup

1. Generate a PAT in Azure DevOps with these scopes:
   - **Work Items**: Read & Write
   - **Code**: Read (for PR queries)
   - **Build**: Read (for pipeline queries)
2. Set the environment variables (see Quick Install above)
3. Test: run `/workitems` in OpenCode

### How It Works

1. You run `/workitems` (or `@devops get my bugs`)
2. OpenCode invokes the **devops** subagent
3. The devops agent loads the **azure-devops-api** skill (comprehensive REST API reference with auth patterns, endpoints, WIQL queries, field names)
4. The agent executes PowerShell commands to query the API
5. Results are formatted as a table

The skill contains every endpoint pattern, WIQL query example, and field name reference — so the agent never has to rediscover the API. It also documents the exact auth header format, error codes, and gotchas.

### Example Queries

```
/workitems                                    # your active items
/workitems all active bugs                    # all open bugs
/workitems tasks in current sprint            # sprint tasks
/workitems changed in the last 3 days         # recent activity
/workitems create a bug titled "Login fails"  # create a work item
@devops check the status of pipeline 42       # pipeline status
@devops get PR comments on repo/PR#100        # PR review comments
```

---

## opencode.json Reference

### New Settings (beyond the original config)

**`"model"` / `"small_model"`**
`azure/gpt-6.1-sol` and `azure/gpt-5.6-luna`. OpenAI's 2026 naming is family + tier: Sol (most capable), Terra, Luna (efficient — roughly the nano class, so a Luna-tier model is the right `small_model` for titles and summaries and the wrong daily driver). The model id is `azure/<catalog id>`; on Azure the deployment name must equal the catalog id unless you map it (`"models": { "gpt-6.1-sol": { "id": "<your-deployment-name>" } }`). Whether a deployment accepts `reasoningEffort` `xhigh`/`max` is decided by Azure, not OpenCode — if a request is rejected, lower it.

**`"skills"`**
`{ "paths": ["~/ai-agent-templates/skills"] }` adds the shared skills folder to the discovery locations; use an absolute path if `~` is not expanded on your platform.

**`tui` / `keybinds` / `theme`** moved out of `opencode.json` into `tui.json` (`OPENCODE_TUI_CONFIG`); OpenCode migrates them automatically but warns.

**`"share": "disabled"`**
Explicitly disables session sharing in the config (in addition to the env var). Belt and suspenders — prevents any accidental sharing of code to `opncd.ai`.

**`"autoupdate": false`**
Disables update checks. Pair with `OPENCODE_DISABLE_AUTOUPDATE=true` env var.

**`"compaction"`**
```json
{
    "auto": true,
    "prune": true,
    "preserve_recent_tokens": 10000
}
```
(The default preserve budget is 25 % of the usable window, clamped to 2,000–15,000 tokens; 10,000 is a deliberate middle.)
- `auto` — automatically compact when context fills up
- `prune` — remove old tool outputs during compaction (saves tokens)
- `preserve_recent_tokens` — keep this many tokens of recent turns verbatim during compaction. **Renamed in OpenCode v1.14.19** (was `reserved`). The old key still works as a deprecated alias.

**`"permission"`**
Granular permission rules. Last matching pattern wins.
- Read operations allowed by default
- Write/edit allowed (you're the only user on AVD)
- Bash uses glob patterns: common dev commands allowed, destructive commands (`rm`, `del`) require confirmation
- Azure DevOps API calls (curl/PowerShell to `dev.azure.com`) auto-allowed
- Web fetch/search denied (air-gapped)
- External directory access requires confirmation

**`"instructions"`**
Additional files loaded as instructions alongside AGENTS.md. Add your project's `CONTRIBUTING.md` or other guidelines.

### Provider Config

See the original guide sections below — unchanged.

**Why the provider key must be `"azure"` (not a custom name)**
The provider key must match `"azure"` exactly — not a custom name like `"gov-gpt"`. OpenCode has a built-in model loader for the `"azure"` provider that automatically uses the correct API format (Responses API) for newer models like Codex. If you use a custom name, the loader doesn't apply and Codex models will fail with "chatCompletion operation does not work with the specified model." Use `"whitelist"` to control which models appear in the picker.

**Why `@ai-sdk/azure` instead of `@ai-sdk/openai-compatible`?**
The `openai-compatible` SDK appends `/v1` to the base URL, which Azure doesn't expect, causing "Resource not found" errors. The `azure` SDK uses `resourceName` and constructs the URL correctly.

**`"env": ["AZURE_OPENAI_API_KEY"]`**
**Required for Codex/Responses API models.** This tells OpenCode to check this environment variable during provider initialization. Without it, the azure provider may not be detected early enough for the Responses API model loader to register, causing Codex models to fall back to Chat Completions and fail. The env var name must match the one you set on your system.

**`"resourceName"`**
Your Azure OpenAI resource name (the subdomain part of `your-resource.openai.azure.com`). Replace `YOUR_RESOURCE_NAME` with the actual name.

**`"apiKey": "{env:AZURE_OPENAI_API_KEY}"`**
References an environment variable rather than hardcoding the key. Never put API keys directly in the config file.

**`"whitelist"`**
Limits the model picker to only the models you define. Without this, you may see extra built-in Azure models from OpenCode's bundled model catalog alongside yours.

**Model keys** (`"gpt-5.5"`, `"gpt-5-mini"`, `"gpt-5.4"`, `"gpt-5.3-codex"`)
Must exactly match your Azure deployment names. If your deployment is named differently (e.g., `"gpt55-prod"`), update the key. **Make sure the deployment name still contains the substring `gpt`** — OpenCode's `system.ts` selects the system prompt by matching that substring; deployments without it get the aggressive 4-line `default.txt` prompt.

**`"limit": { "context": 272000, "output": 128000 }`** (for GPT-5.5)
Tells OpenCode the model's token limits. **Capped at 272,000** rather than the model's actual 1,050,000 because OpenAI charges 2× input and 1.5× output for the entire request once a single prompt crosses 272K input tokens. Compaction will fire well below the cap. Raise only if you genuinely need the headroom.

**`"options": { "reasoningEffort": "medium", "textVerbosity": "low" }`** (GPT-5.5)
Per OpenAI's prompt guidance, GPT-5.5 defaults to `medium` reasoning effort and benefits from explicit `low` verbosity for coding work. Escalating to `high` can regress quality with weak stopping criteria or open-ended tools. If you deploy a Pro tier, add a separate model entry with `reasoningEffort: "high"` for it.

**GPT-5.5 OAuth context-limit fix:** OpenCode versions before v1.14.25 misreported GPT-5.5's context budget on OAuth-authenticated sessions (capped it at 256K = 262,144 tokens). If you've seen the model report `262144` as its limit, update OpenCode to v1.14.25 or later. GPT-5.4 doesn't expose its limit on request because it wasn't trained with that introspection — only 5.5 does.

---

## Codex Models (`gpt-5.3-codex`)

Codex models require the **Responses API** (`/openai/responses`), not Chat Completions. OpenCode's built-in `azure` provider loader handles this automatically — it defaults to the Responses API for all models.

**This only works if your provider key is `"azure"`.** If you use a custom name (e.g., `"gov-gpt"`), OpenCode won't apply the azure-specific loader and will fall back to Chat Completions, causing the error: "chatCompletion operation does not work with the specified model."

To use Codex (or any model requiring Responses API):
1. Ensure your provider key is `"azure"` (as in the provided config)
2. Include `"env": ["AZURE_OPENAI_API_KEY"]` in the provider config (this ensures the Responses API loader registers during initialization — without it, the loader may silently fail to register due to a timing issue in the provider initialization order)
3. Add your model entry in `"models"` matching your Azure deployment name
4. Switch to it with `/model` or set it as default: `"model": "azure/gpt-5.3-codex"`

See also: [GitHub issue #13999](https://github.com/sst/opencode/issues/13999) for upstream tracking (different root cause — Cognitive Services endpoints — but same symptom).

---

## Skills

Skills are reusable instruction sets (a folder with a `SKILL.md`) that agents load when a task matches the skill's description. OpenCode discovers them in `.opencode/skills/`, `~/.config/opencode/skills/`, `.claude/skills/`, `~/.claude/skills/`, `.agents/skills/`, `~/.agents/skills/`, plus any folder listed under `skills.paths` in `opencode.json` (`OPENCODE_DISABLE_EXTERNAL_SKILLS` drops the `.claude`/`.agents` locations; `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` just those).

### Included Skills

| Skill | Where | Purpose |
|-------|-------|---------|
| `azure-devops-api` | `opencode/skills/` (copied) | Complete REST API reference — auth, work items, WIQL, pipelines, repos, field names, error handling |
| `azure-cli` | [`../skills/`](../skills/) (shared, read in place) | Login and scope first, inventory without filters, JMESPath `--query` rules, what empty results and errors mean |
| `session-notes` | shared | What to record, when to update, the layout of the session-notes file |
| `kb-capture` | shared | How to give a finding back to the knowledge base, in the house format |

### Creating Custom Skills

Create a directory with a `SKILL.md` file:

```
~/.config/opencode/skills/my-skill/SKILL.md
```

Format:
```markdown
---
name: my-skill
description: What this skill does, in the words a person would use to ask for it
---
## Content
```

The same folder layout loads in Codex CLI (`[[skills.config]]`) and Claude Code (`~/.claude/skills/`), which is why the shared ones live at the repository root.

## Content

Your instructions, reference material, checklists, etc.
```

Skill ideas for your environment:
- **deployment-checklist** — step-by-step deployment procedures
- **code-standards** — org-specific naming conventions and patterns
- **incident-response** — runbook for investigating production issues
- **onboarding** — project setup guide for new team members

---

## Custom Commands

Commands are slash-command shortcuts. They live in `~/.config/opencode/commands/<name>.md`.

### Included Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/workitems` | devops | Query Azure DevOps work items |
| `/review` | code-reviewer | Run a code review on changes |
| `/test` | qa-tester | Write and run tests |
| `/document` | scribe | Generate documentation |
| `/security-scan` | security-auditor | Security audit |
| `/design` | architect | Architecture analysis |

### Command Syntax

In the TUI, commands accept arguments after the command name:
```
/workitems bugs assigned to me in the current sprint
/review src/controllers/
/test --focus auth module
/document API endpoints
/security-scan the payment processing code
/design should we use event sourcing for audit logs
```

### Creating Custom Commands

```markdown
---
description: What this command does
agent: which-agent       # optional: routes to a specific agent
model: azure/gpt-5-mini  # optional: override model for this command
---
Prompt template here.

$ARGUMENTS    # replaced with everything after the command name
$1 $2 $3      # positional arguments
!`git status`  # inject shell output
@filename      # inject file content
```

---

## Outbound Network Calls

OpenCode makes several outbound calls that may be blocked in restricted environments or that you may want to disable for privacy:

| Domain | Purpose | Disable with |
|---|---|---|
| `opncd.ai` | Session sharing — sends full prompts, code, and diffs | `OPENCODE_DISABLE_SHARE=true` + `"share": "disabled"` |
| `models.dev` | Model catalog fetch every 60 min | `OPENCODE_DISABLE_MODELS_FETCH=true` |
| `registry.npmjs.org` | Update checks | `OPENCODE_DISABLE_AUTOUPDATE=true` |
| `api.github.com` | LSP binary downloads | `OPENCODE_DISABLE_LSP_DOWNLOAD=true` |
| `github.com` | ripgrep, tree-sitter WASM | `OPENCODE_DISABLE_LSP_DOWNLOAD=true` |

**Session sharing is the critical one** — once a share exists, `opncd.ai` receives all messages, tool call results (including file contents), and diffs. It is not prominently documented. Always disable it.

**On Windows AVD:** Note that Node.js uses OpenSSL, not Windows schannel — this means Node.js can reach GitHub and npm even when curl cannot (SSL inspection blocks curl but not Node). The env var flags are necessary even if curl-based tests suggest those domains are blocked.

**`NO_PROXY=localhost,127.0.0.1`** is critical — OpenCode's TUI communicates with its own local HTTP server. Without this, proxy settings can break the TUI entirely.

---

## AGENTS.md Reference

### Why this AGENTS.md is short — and what was added in Oct 2026

The default AGENTS.md is tuned for the GPT-5.6 / GPT-6 families. OpenAI's guidance for them: leaner prompts score higher and spend far fewer tokens; state autonomy boundaries once; no "think harder" coaching; the newest models follow AGENTS.md and skills closely and pause early on contradictory instructions. OpenCode injects this file into the system prompt on every step, so nothing in it is lost at compaction.

Added in Oct 2026 after a real incident (a Luna-tier model ran `az … --query` with a malformed expression, got `[]`, and reported "your account has no access"): **Evidence Rules (tool results)** — empty is not "no access", bisect the command, quote the command and output, three different attempts before a hand-back; investigation framing in Role/Goal/Stop rules; **Session Notes**, **Knowledge Base**, **Skills** and **Azure CLI** sections that point at the shared skills and the session-notes plugin.

**For older models** (gpt-5.1/5.2 deployments): use the GPT-5.1 profile, which keeps the heavier reasoning coaching those models still need, plus the same additions.

### Key Differences from Codex AGENTS.md

**Compaction** — OpenCode uses two-tier context management: per-turn pruning (cheap, automatic) clears old tool outputs every loop, and full LLM compaction fires only at overflow. With GPT-5.5 capped at 272K (under the 2× pricing cliff), full compaction rarely fires. Without the [patched fork](#pre-built-windows-binaries), the compaction summarizer runs with an empty system prompt and doesn't preserve AGENTS.md rules — so instructions can still be silently lost on the rare occasion compaction does fire.

**Plan mode** — Activated with **Tab** in the composer. Switches to a read-only exploration mode. Optional with the Sol tiers — they handle ambiguity well without forced planning. Useful when you want to confirm scope before letting it run.

**`/compact`** — Manual compaction command. Run proactively when context is getting full.

### Session Management Strategy

Even with compaction, long sessions can lose instruction context:

1. **Keep sessions shorter.** Treat sessions as disposable. Start fresh often.
2. **Session context file is your continuity.** Not a nice-to-have — it's how you carry context between sessions.
3. **Restart, don't rescue.** When behavior degrades, start fresh with context notes.
4. **Watch the token counter.** When usage is high, wrap up or start fresh.
5. **Use `/compact` proactively.** Don't wait for auto-compaction.
6. **Use the patched fork** if possible — see Building from Source below.

---

**Session notes, enforced (Oct 2026).** `plugins/session-notes.js` is a local plugin (drop it in `~/.config/opencode/plugins/`, no `plugin:` entry needed): on `session.created` it injects the notes file as context (`client.session.prompt` with `noReply`), on `session.idle` it sends one follow-up prompt when `~/.config/opencode/session-notes.md` (or `SESSION_NOTES`) is missing or more than 30 minutes old (one nudge per 30-minute cooldown per session, so it cannot loop), and at compaction it appends the notes rule to the compaction context (`experimental.session.compacting`). It is the OpenCode form of the Stop/PreCompact hooks the Codex and Claude Code templates use. `SESSION_NOTES_GUARD=off` disables the nudge. The plugin was checked against the plugin API types and exercised with a fake client, not in a live OpenCode session — report problems at the repository.

## Keyboard Reference

| Action | Keybind |
|--------|---------|
| Exit | `ctrl+c`, `ctrl+d`, `<leader>q` |
| New session | `<leader>n` |
| List sessions | `<leader>l` |
| Switch primary agent | `Tab` / `Shift+Tab` |
| List agents | `<leader>a` |
| Switch model | `<leader>m` |
| Cycle model variant | `ctrl+t` |
| Command palette | `ctrl+p` |
| Compact session | `<leader>c` |
| Undo | `<leader>u` |
| Redo | `<leader>r` |
| Export session | `<leader>x` |
| Open external editor | `<leader>e` |
| Toggle sidebar | `<leader>b` |
| Toggle help | `<leader>h` |
| Status view | `<leader>s` |
| Timeline | `<leader>g` |
| Copy messages | `<leader>y` |
| New line in input | `Shift+Return` (requires Terminal fix) |
| Interrupt | `Escape` |
| Submit | `Return` |
| Enter child session | `<leader>+Down` |
| Next/prev child | `Right` / `Left` |
| Return to parent | `Up` |

Leader key is `ctrl+x` by default.

---

## Pre-Built Windows Binaries

Pre-built Windows x64 binaries are available as GitHub Releases on the [fork](https://github.com/jblenman/opencode). Two versions:

| Release | Branch | What it does |
|---------|--------|--------------|
| [Hardened Build](https://github.com/jblenman/opencode/releases/tag/hardened-build-2026-03-12) | `hardened/federal-secure` | Compaction fix **+ all security flags baked in** (recommended) |
| [Compaction Fix Only](https://github.com/jblenman/opencode/releases/tag/compaction-fix-2026-03-12) | `fix/compaction-preserve-instructions` | Standard OpenCode with compaction fix ([PR #16959](https://github.com/anomalyco/opencode/pull/16959)) |

Cross-compiled from macOS using Bun 1.3.10 targeting `bun-windows-x64`.

### Installation (Windows AVD)

```powershell
# Option 1: Download from the cloned fork repo's releases page in a browser
# Option 2: If gh CLI is available:
gh release download hardened-build-2026-03-12 --repo jblenman/opencode --pattern "*.zip" --dir "$HOME\Downloads"

# Extract and place on PATH
Expand-Archive "$HOME\Downloads\opencode-hardened-windows-x64.zip" -DestinationPath "$HOME\bin" -Force

# Verify
& "$HOME\bin\opencode.exe" --version

# Ensure ripgrep is installed (hardened build won't download it)
scoop install ripgrep   # or: choco install ripgrep
```

### Hardened Build — What's Changed

| Feature | Outbound target | Status in hardened build |
|---|---|---|
| Session sharing | `opncd.ai` | **Removed** — hardcoded `disabled = true` in source |
| Auto-update checks | npmjs, GitHub, brew, choco, scoop | **Removed** — flag hardcoded |
| Model catalog fetch | `models.dev` | **Removed** — uses bundled snapshot |
| LSP binary downloads | GitHub (9+ repos) | **Removed** — flag hardcoded |
| External skill loading | Local filesystem scan | **Removed** — flag hardcoded |
| Exa web/code search | `mcp.exa.ai` | **Removed** — flag hardcoded to `false` |
| OpenTelemetry spans | Wherever OTLP is configured | **Removed** — hardcoded `false` |
| Ripgrep download | GitHub | **Removed** — errors if `rg` not on PATH |
| LLM API calls | Your Azure/provider endpoint | **Unchanged** — this is the core function |

Environment variables for these features are ignored — the values are constants in the source. **No security env vars needed** with the hardened build.

The compaction-fix-only build retains all standard OpenCode behavior — you still need the `OPENCODE_DISABLE_*` env vars for restricted environments.

### Compaction Fix Details

Both builds include this fix. Preserves AGENTS.md instructions across context compaction:

1. **Compaction system prompt** — passes project instructions into the compaction LLM call (was `system: []`)
2. **Summary template** — adds "Active Project Instructions" section to capture behavioral rules
3. **Post-compaction injection** — injects instructions as `<system-reminder>` message after compaction

### Windows Build Note

**Bun standalone builds do not work natively on Windows.** Per [OpenCode docs](https://opencode.ai/docs): "Support for installing OpenCode on Windows using Bun is currently in progress." These binaries are cross-compiled from macOS.

### Building from Source (macOS/Linux)

If you need to rebuild (e.g., after upstream changes):

```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Clone and build
git clone -b hardened/federal-secure https://github.com/jblenman/opencode.git
cd opencode
bun install
cd packages/opencode
bun run script/build.ts    # builds all platforms including Windows x64

# Windows binary is at:
# dist/opencode-windows-x64/bin/opencode.exe
```

---

## Recent OpenCode Updates (checked 2026-10-05)

The repository moved to **github.com/anomalyco/opencode** (sst/opencode redirects; default branch `dev`). Latest release **v1.18.34 (Sep 30 2026)**, bundling `@ai-sdk/azure` 3.0.93.

| Change | Notes |
|---|---|
| Models | models.dev lists the GPT-5.6 Sol/Terra/Luna, GPT-6 Astra/Sol/Luna and GPT-6.1 Sol families for both `openai` and `azure` (1.05M context, 922K input, 128K output); OpenCode offers `reasoningEffort` variants from the catalog (`low`…`max`) |
| Config schema | `tui`, `keybinds`, `theme` moved to `tui.json`; `mode` → `agent`, `autoshare` → `share`, agent `tools` → `permission`, `maxSteps` → `steps` (deprecated, auto-migrated); new `skills.paths/urls`, `plugin[]`, `subagent_depth`, `tool_output` |
| Plugins | local JS/TS plugins auto-load from `.opencode/plugins/` and `~/.config/opencode/plugins/`; hooks incl. `event` (`session.idle`, `session.created`, `session.compacted`…), `tool.execute.before/after`, `permission.ask`, `experimental.session.compacting`; the SDK's `session.prompt` with `noReply` injects context |
| Instructions | project `AGENTS.md` → `CLAUDE.md`; global `~/.config/opencode/AGENTS.md` else `~/.claude/CLAUDE.md`; injected into the system prompt every step (no instruction loss at compaction) |
| Air-gap flags | `OPENCODE_DISABLE_AUTOUPDATE`, `OPENCODE_DISABLE_MODELS_FETCH` (+ `OPENCODE_MODELS_URL`), `OPENCODE_DISABLE_LSP_DOWNLOAD`, `OPENCODE_DISABLE_DEFAULT_PLUGINS`, `OPENCODE_DISABLE_EXTERNAL_SKILLS`, `OPENCODE_PURE` / `--pure`; `share: "disabled"`; managed config dirs (`%ProgramData%\opencode`, `/etc/opencode`) |
| V2 config | a next-generation config shape (`permissions`, `plugins`, `agents`, `compaction.keep`) exists in the source and errors on the current CLI ("run opencode2") — stay on the V1 keys used here |

Earlier (Apr–May 2026): v1.14.30 instruction precedence (global before project/skill), v1.14.25 GPT-5.5 context limits, v1.14.19 `reserved` → `preserve_recent_tokens`, Azure prompt caching by default.

## Known Issues (reviewed 2026-10-05)

- **Bun builds on Windows** — not supported yet. Use cross-compiled binaries from the fork.
- **Codex models** require provider key `"azure"` exactly — custom names don't inherit the Responses API loader.
- **Instruction loss during compaction** — historical; the current source rebuilds the system prompt (instructions included) on every step. The hardened fork's fix ([PR #16959](https://github.com/anomalyco/opencode/pull/16959)) matters only on older builds. Less impactful anyway since compaction rarely fires under the 272K cap.
- **`openai-compatible` provider** causes "Resource not found" on Azure — always use `@ai-sdk/azure`.
- **`az devops` CLI** doesn't work reliably on AVD — use REST API via the devops agent and azure-devops-api skill instead.
- **Anthropic OAuth** removed in early 2026 — Claude requires a direct API key.
- **Deployment name must contain `gpt`** — OpenCode's prompt routing matches on substring; otherwise model gets the aggressive `default.txt` "fewer than 4 lines" prompt.

---

## File Layout Reference

```
~/.config/opencode/
├── opencode.json                          # Main config
├── AGENTS.md                              # Global coaching (reasoning, git safety, etc.)
├── agents/                                # Agent team
│   ├── code-reviewer.md                   #   Code quality + security review
│   ├── qa-tester.md                       #   Test writing + execution
│   ├── scribe.md                          #   Documentation generation
│   ├── researcher.md                      #   Codebase exploration
│   ├── security-auditor.md                #   OWASP + vulnerability scanning
│   ├── architect.md                       #   Design decisions + trade-offs
│   └── devops.md                          #   Azure DevOps REST API integration
├── skills/
│   └── azure-devops-api/
│       └── SKILL.md                       #   Complete DevOps REST API reference
└── commands/
    ├── workitems.md                       #   /workitems — query DevOps
    ├── review.md                          #   /review — code review
    ├── test.md                            #   /test — write + run tests
    ├── document.md                        #   /document — generate docs
    ├── security-scan.md                   #   /security-scan — security audit
    └── design.md                          #   /design — architecture analysis
```
