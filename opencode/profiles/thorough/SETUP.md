# OpenCode — Thorough Profile

For users who want depth-over-speed: GPT-5.5 at `reasoning_effort = "high"` plus an Investigation Requirements coaching block that forces the model to read callers, check tests, and surface cross-file impact before implementing.

## When to use this profile

**Reach for this profile when:**
- You're working in unfamiliar code where impact isn't obvious
- The change touches a public interface (exported function, API, schema, config)
- You're doing design-affecting work (data model, persistence, error handling)
- You've noticed the default profile missing impact in similar work
- You're willing to wait ~2× per turn to land changes correctly the first time

**Stick with the default profile when:**
- The task scope is clear and localized (typos, log lines, trivial renames)
- You're iterating quickly and prefer fast turns
- You're doing exploratory or throwaway work
- Per-turn latency matters more than per-task wall-clock time

The default profile matches OpenAI's official GPT-5.5 guidance and is the right team-wide default. This profile is an opinionated overlay for personal preference or specific work contexts.

## Tradeoffs

| Aspect | Default | Thorough |
|---|---|---|
| `reasoningEffort` | `medium` | `high` |
| Per-turn latency | ~baseline | ~1.5–2× |
| Token cost per turn | ~baseline | ~1.3–1.7× (more reasoning + more reads) |
| AGENTS.md weight | Light | Light + Investigation Requirements block |
| Routine `@researcher`/`@architect` use | Optional | Expected for non-trivial changes |
| Per-task wall-clock | Faster *if* the task is clear | Often faster *if* the task is ambiguous (fewer redo cycles) |

The thorough profile bets that on harder tasks, the time spent investigating saves more time than it costs. That bet is right for some work and wrong for other work — use judgment.

## Prerequisites

- Azure AI Foundry deployment of `gpt-5.5` (and ideally `gpt-5-mini` as small_model)
- Node.js / npm
- ripgrep (`rg`) on PATH
- OpenCode v1.14.25 or later (for correct GPT-5.5 OAuth context limits)

## 1. Environment Variables

Same as the default profile. If you've already set these, skip ahead.

```powershell
# Azure credentials
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "your-key", "User")

# Block unnecessary outbound calls (AVD)
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_SHARE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_MODELS_FETCH", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_AUTOUPDATE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_LSP_DOWNLOAD", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_EXTERNAL_SKILLS", "true", "User")

# Critical: TUI uses a local HTTP server — must bypass proxy
[Environment]::SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1", "User")

# Azure DevOps (optional)
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

# Config + coaching (thorough profile)
New-Item -ItemType Directory -Path $dst -Force
Copy-Item "$repo\opencode\profiles\thorough\opencode.json" "$dst\opencode.json"
Copy-Item "$repo\opencode\profiles\thorough\AGENTS.md" "$dst\AGENTS.md"

# Agent team (shared with default profile)
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

## 4. Test

```bash
opencode
# Should connect to Azure and show "GPT-5.5 (thorough)" in the model picker
```

Try a task you'd expect to require investigation — e.g., renaming a public function in a multi-file project. The agent should read at least one caller before suggesting the change, and surface what else might be affected.

## Switching Between Profiles

The default and thorough profiles share the same agent team, commands, and skills — only `opencode.json` and `AGENTS.md` differ. To switch:

```powershell
# Switch to thorough
Copy-Item "$HOME\ai-agent-templates\opencode\profiles\thorough\opencode.json" "$HOME\.config\opencode\opencode.json"
Copy-Item "$HOME\ai-agent-templates\opencode\profiles\thorough\AGENTS.md"     "$HOME\.config\opencode\AGENTS.md"

# Switch back to default
Copy-Item "$HOME\ai-agent-templates\opencode\opencode.json" "$HOME\.config\opencode\opencode.json"
Copy-Item "$HOME\ai-agent-templates\opencode\AGENTS.md"     "$HOME\.config\opencode\AGENTS.md"
```

For per-project overrides, you can keep the default global config and place a project-level `AGENTS.md` with the Investigation Requirements block in repos where you want the thorough behavior.

## Codex CLI Equivalent

Codex CLI doesn't need a separate profile directory — its `[profiles.deep]` block in the main `config.toml` already configures the equivalent behavior:

```bash
codex --profile deep
```

That gives you `reasoning_effort = "high"` with detailed reasoning summaries. To get the Investigation Requirements coaching on top, copy this profile's AGENTS.md to `~/.codex/AGENTS.md` (Codex auto-discovers it the same way OpenCode does).

You can also raise reasoning live in the Codex TUI with `Alt+.` (v0.124.0+) for a single turn without committing to the deep profile.

## Differences from Default Profile

| Aspect | Default | Thorough |
|---|---|---|
| Model | gpt-5.5 | gpt-5.5 (same) |
| `options.reasoningEffort` | `medium` | `high` |
| `options.textVerbosity` | `low` | `low` (same) |
| Investigation Requirements block | Not present | Present — explicit prescriptions for reads, grep, caller lookups |
| `@researcher` use | Optional | Expected for non-trivial changes |
| `@architect` use | Judgment | Mandatory for cross-component changes |
| Pushback expectation | Implicit | Explicit "say so before implementing" rule |
| Per-turn token cost | Baseline | ~1.3–1.7× baseline |
