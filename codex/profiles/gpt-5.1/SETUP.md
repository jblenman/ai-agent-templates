# Codex CLI — GPT-5.1 Federal Setup

Setup guide for Codex CLI on a federal government system with only GPT-5.1 available. Less locked down than AVD but still security-conscious.

## Prerequisites

- Azure AI Foundry deployment of `gpt-5.1`
- Node.js / npm
- Codex CLI: `npm install -g @openai/codex`

## 1. Environment Variables

```powershell
# Azure credentials
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "your-key", "User")

# Critical: if using a proxy, TUI needs localhost excluded
[Environment]::SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1", "User")
```

Restart your terminal after setting env vars.

## 2. Install Config Files

```powershell
$repo = "$HOME\ai-agent-templates"
$dst  = "$HOME\.codex"

# Clone templates repo (if not already cloned)
git clone https://github.com/jblenman/ai-agent-templates.git $repo

# Config + coaching (gpt-5.1 profile)
New-Item -ItemType Directory -Path $dst -Force
Copy-Item "$repo\codex\profiles\gpt-5.1\config.toml" "$dst\config.toml"
Copy-Item "$repo\codex\profiles\gpt-5.1\AGENTS.md" "$dst\AGENTS.md"
```

## 3. Update Config

Edit `~/.codex/config.toml`:
- In the `[model_providers.azure]` section, replace `YOUR_RESOURCE_NAME` with your Azure resource name
- Codex doesn't support `{env:}` substitution in `base_url` — it must be the literal URL

## 4. Verify Context Limits

The config sets `tool_output_token_limit = 25000`, which is conservative for a 128k context window. Check your Azure deployment's actual limits — if gpt-5.1 has a larger window, you can increase this (aim for ~20% of context).

## 5. Windows Terminal: Fix Shift+Enter

Add to Windows Terminal `settings.json` (Settings > Open JSON file) under `"actions"`:

```json
{
    "command": { "action": "sendInput", "input": "\u001b[13;2u" },
    "id": "User.sendInput.ShiftEnterCustom"
}
```

## 6. Test

```bash
codex
# Should connect to Azure and use gpt-5.1
```

## Outbound Network

| Target | Status | Why |
|--------|--------|-----|
| Azure LLM provider | Allowed | Core function |
| Web search (cached) | Allowed | Routed through Azure API, not direct — helps 5.1 look things up |
| Analytics/feedback | Blocked | Disabled in config |
| Update checks | Blocked | `check_for_update_on_startup = false` |

## Differences from Default Config

| Aspect | Default | This Profile |
|--------|---------|--------------|
| Model | Uncommented (user sets) | `gpt-5.1` |
| `review_model` | gpt-5-mini | gpt-5.1 (only model available) |
| `tool_output_token_limit` | 32000 | 25000 (conservative for 128k context) |
| `web_search` | `"cached"` | `"cached"` (same — 5.1 needs the lookup ability) |
| AGENTS.md coaching | Standard | Extra aggressive (5.1 needs more guardrails) |

## GPT-5.1 Tips

- **Be explicit in prompts** — "analyze this, consider 2+ approaches, recommend the best" instead of "fix this"
- **Use `codex --profile deep`** for hard problems — maximum reasoning effort
- **Review its work** — 5.1 is more likely to produce plausible-but-wrong code
- **Keep sessions shorter** — `codex --resume` picks up where you left off
- **The AGENTS.md coaching is critical** — don't trim it
- **Use multi-agent** — let it delegate subtasks to parallel agents for structured workflow
