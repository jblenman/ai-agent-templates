# OpenCode — GPT-5.1 Federal Setup

Setup guide for OpenCode on a federal government system with only GPT-5.1 available. Less locked down than AVD but still security-conscious.

## Prerequisites

- Azure AI Foundry deployment of `gpt-5.1`
- Node.js / npm
- ripgrep (`rg`) on PATH
- OpenCode: `npm install -g opencode`

## 1. Environment Variables

```powershell
# Azure credentials
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "your-key", "User")

# Security — disable non-essential outbound calls
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_SHARE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_MODELS_FETCH", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_AUTOUPDATE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_EXTERNAL_SKILLS", "true", "User")
# LSP downloads from GitHub are allowed (well-known source, helps 5.1 with language intelligence)
# To disable if needed:
# [Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_LSP_DOWNLOAD", "true", "User")

# Critical: TUI uses a local HTTP server — must bypass proxy
[Environment]::SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1", "User")

# Azure DevOps (optional — for agent team /workitems command)
# [Environment]::SetEnvironmentVariable("AZURE_DEVOPS_PAT", "your-pat", "User")
# [Environment]::SetEnvironmentVariable("AZURE_DEVOPS_ORG", "your-org", "User")
# [Environment]::SetEnvironmentVariable("AZURE_DEVOPS_PROJECT", "your-project", "User")
```

Restart your terminal after setting env vars.

## 2. Install Config Files

```powershell
$repo = "$HOME\ai-agent-templates"
$dst  = "$HOME\.config\opencode"

# Clone templates repo (if not already cloned)
git clone https://github.com/jblenman/ai-agent-templates.git $repo

# Config + coaching (gpt-5.1 profile)
New-Item -ItemType Directory -Path $dst -Force
Copy-Item "$repo\opencode\profiles\gpt-5.1\opencode.json" "$dst\opencode.json"
Copy-Item "$repo\opencode\profiles\gpt-5.1\AGENTS.md" "$dst\AGENTS.md"

# Agent team (shared — update models below)
New-Item -ItemType Directory -Path "$dst\agents" -Force
Copy-Item "$repo\opencode\agents\*.md" "$dst\agents\"

# Commands (shared)
New-Item -ItemType Directory -Path "$dst\commands" -Force
Copy-Item "$repo\opencode\commands\*.md" "$dst\commands\"

# Skills (optional — for Azure DevOps integration)
# New-Item -ItemType Directory -Path "$dst\skills\azure-devops-api" -Force
# Copy-Item "$repo\opencode\skills\azure-devops-api\SKILL.md" "$dst\skills\azure-devops-api\SKILL.md"
```

## 3. Update Config

Edit `~/.config/opencode/opencode.json`:
- Replace `YOUR_RESOURCE_NAME` with your Azure resource name

## 4. Update Agent Models to GPT-5.1

The shared agent files reference gpt-5.2/5.4/5-mini. On a 5.1-only system, update them all:

```powershell
# Update all agent files to use gpt-5.1
Get-ChildItem "$HOME\.config\opencode\agents\*.md" | ForEach-Object {
    (Get-Content $_.FullName) -replace 'model: azure/gpt-5\.\d[\w.-]*', 'model: azure/gpt-5.1' |
    Set-Content $_.FullName
}
```

## 5. Verify Context Limits

The config assumes **128k context / 32k output** for gpt-5.1. Check your Azure deployment's actual limits and update `provider.azure.models.gpt-5.1.limit` in `opencode.json` if they differ.

## 6. Test

```bash
opencode
# Should connect to Azure and show gpt-5.1 in the model picker
```

## Outbound Network

| Target | Status | Why |
|--------|--------|-----|
| Azure LLM provider | Allowed | Core function |
| GitHub (LSP downloads) | Allowed | Well-known; language intelligence helps 5.1 |
| `opncd.ai` (session sharing) | Blocked | Sends full prompts/code to third party |
| `models.dev` (model catalog) | Blocked | Non-essential |
| npm (auto-update) | Blocked | Controlled updates only |
| `mcp.exa.ai` (web search) | Blocked | Off by default |
| External skills | Blocked | Filesystem scan, unnecessary |

## Differences from Default (AVD) Config

| Aspect | Default (AVD) | This Profile |
|--------|---------------|--------------|
| Model | gpt-5.2 / 5.3-codex / 5.4 | gpt-5.1 only |
| `small_model` | gpt-5-mini | Removed (only one model available) |
| LSP downloads | Blocked (air-gapped) | Allowed (GitHub accessible) |
| AGENTS.md coaching | Standard | Extra aggressive (5.1 needs more guardrails) |
| Compaction reserve | 10000 | 15000 (5.1's smaller context needs more buffer) |
| Azure DevOps permissions | Included | Optional (uncomment if needed) |

## GPT-5.1 Tips

- **Use plan mode** (Tab) before implementing — 5.1 benefits more from the forced read-first step
- **Keep sessions shorter** — compaction fires more often with 128k context
- **Be explicit in prompts** — "analyze this, consider 2+ approaches, recommend the best" instead of "fix this"
- **Review its work** — 5.1 is more likely to produce plausible-but-wrong code
- **The AGENTS.md coaching is critical** — don't trim it
- **Use the agent team** — structured delegation compensates for 5.1's weaker judgment
