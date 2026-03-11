# OpenCode — Configuration Guide

Reference for `opencode.json` and `AGENTS.md` settings, with reasoning behind each choice and alternatives.

## Installation

```bash
# Config
mkdir -p ~/.config/opencode
curl -o ~/.config/opencode/opencode.json https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/opencode/opencode.json

# Edit opencode.json — replace YOUR_RESOURCE_NAME with your Azure resource name

# Set your API key as an environment variable (Windows)
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "your-key", "User")

# Coaching file
curl -o ~/.config/opencode/AGENTS.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/opencode/AGENTS.md
```

### Required environment variables (Windows AVD)

Set these as User environment variables to block unnecessary outbound calls:

```powershell
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_SHARE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_MODELS_FETCH", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_AUTOUPDATE", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_LSP_DOWNLOAD", "true", "User")
[Environment]::SetEnvironmentVariable("OPENCODE_DISABLE_EXTERNAL_SKILLS", "true", "User")
```

---

## opencode.json Reference

### `"model"`
The default model to use. Format is `"provider-key/model-key"` matching the keys you define in `"provider"`.
- Change to `"gov-gpt/gpt-5-mini"` for a faster, cheaper default
- The model can be changed mid-session with `/model`

### `"disabled_providers"`
Removes providers from the model picker. `"opencode"` removes the built-in Zen/OpenCode gateway, which requires a paid OpenCode subscription and has no use on Azure.
- Add other built-in provider names you don't need to keep the model list clean

### `"provider"`
Defines custom LLM providers. Each key becomes a provider ID used in `"model"`.

**Why `@ai-sdk/azure` instead of `@ai-sdk/openai-compatible`?**
The `openai-compatible` SDK appends `/v1` to the base URL, which Azure doesn't expect, causing "Resource not found" errors. The `azure` SDK uses `resourceName` and constructs the URL correctly.

**`"resourceName"`**
Your Azure OpenAI resource name (the subdomain part of `your-resource.openai.azure.com`). Replace `YOUR_RESOURCE_NAME` with the actual name.

**`"apiKey": "{env:AZURE_OPENAI_API_KEY}"`**
References an environment variable rather than hardcoding the key. Never put API keys directly in the config file.
- Change the env var name to match whatever variable your org uses

**Model keys** (`"gpt-5.2"`, `"gpt-5-mini"`)
Must exactly match your Azure deployment names. If your deployment is named differently (e.g., `"gpt52-prod"`), update the key.

**`"limit": { "context": 400000, "output": 128000 }`**
Tells OpenCode the model's token limits. These are used to calculate context usage display. Set them accurately for your model version.

---

### Why no `gpt-5.3-codex`?

Codex models require the **Responses API** (`/openai/responses`), but OpenCode's `@ai-sdk/azure` defaults to Chat Completions. This causes an error: "chatCompletion operation does not work with the specified model." Track [GitHub issue #13999](https://github.com/sst/opencode/issues/13999) for a fix.

`gpt-5.2` is a strong alternative — very capable for coding tasks.

---

## Outbound Network Calls

OpenCode makes several outbound calls that may be blocked in restricted environments or that you may want to disable for privacy:

| Domain | Purpose | Disable with |
|---|---|---|
| `opncd.ai` | Session sharing — sends full prompts, code, and diffs | `OPENCODE_DISABLE_SHARE=true` |
| `models.dev` | Model catalog fetch every 60 min | `OPENCODE_DISABLE_MODELS_FETCH=true` |
| `registry.npmjs.org` | Update checks | `OPENCODE_DISABLE_AUTOUPDATE=true` |
| `api.github.com` | LSP binary downloads | `OPENCODE_DISABLE_LSP_DOWNLOAD=true` |
| `github.com` | ripgrep, tree-sitter WASM | `OPENCODE_DISABLE_LSP_DOWNLOAD=true` |

**Session sharing is the critical one** — once a share exists, `opncd.ai` receives all messages, tool call results (including file contents), and diffs. It is not prominently documented. Always disable it.

**On Windows AVD:** Note that Node.js uses OpenSSL, not Windows schannel — this means Node.js can reach GitHub and npm even when curl cannot (SSL inspection blocks curl but not Node). The env var flags are necessary even if curl-based tests suggest those domains are blocked.

---

## AGENTS.md Reference

### Key differences from Codex AGENTS.md

**Compaction** — OpenCode uses LLM-based compaction (not simple truncation). When the context window fills, it sends the conversation to a summarizer and continues from the summary. However, without the [patched fork](#building-from-source-patched-fork), the compaction summarizer runs with an empty system prompt and doesn't preserve AGENTS.md rules — so instructions can still be silently lost. The Session Management section addresses this.

**Plan mode** — OpenCode's plan mode is activated with **Tab** in the composer. This switches to a read-only exploration mode where the model can look at files without making changes. Use it before any non-trivial implementation. The Codex equivalent is prompting explicitly ("explore only, don't make changes yet").

**`/compact`** — OpenCode's manual compaction command. Run it proactively when the context window starts getting full. This triggers LLM summarization rather than waiting for auto-compaction (which can happen mid-response).

### Session management strategy

Even with compaction, long sessions can lose instruction context. These practices help:

1. **Keep sessions shorter.** Treat sessions as disposable. Start fresh often.
2. **Session context file is your continuity.** Not a nice-to-have — it's how you carry context between sessions. The compaction summary captures what you did, but the session context file carries the full picture.
3. **Restart, don't rescue.** When behavior degrades (shallow responses, ignoring git rules, losing project context), starting a fresh session with your context notes is dramatically more effective than trying to re-inject instructions into a degraded session.
4. **Watch the token counter.** When usage is high, wrap up or start fresh.
5. **Use `/compact` proactively.** Don't wait for auto-compaction — triggering it manually gives you control over when summarization happens.
6. **Use the patched fork.** The [build-from-source instructions](#building-from-source-patched-fork) describe how to run a version that preserves AGENTS.md across compaction.

### Reasoning coaching

The same coaching as the Codex AGENTS.md applies. GPT-5.2 gives the first plausible answer without self-correcting unless specifically instructed not to. The explicit "2 alternatives" and "question assumptions" requirements directly counter this. Vague instructions ("think carefully") are less effective than specific requirements.

OpenCode also supports an `AGENTS.md` reasoning section. Plan mode (Tab) provides a natural "think first" phase — use it before any implementation.

---

## Building from Source (Hardened Fork)

Two branches are available on the [fork](https://github.com/jblenman/opencode):

| Branch | What it does |
|---|---|
| `fix/compaction-preserve-instructions` | Compaction fix only ([PR #16959](https://github.com/anomalyco/opencode/pull/16959)) |
| `hardened/federal-secure` | Compaction fix **+ all security flags baked in** (recommended for gov/restricted environments) |

The hardened branch bakes all security settings into the source code so they **cannot be overridden** by environment variables or config. The only outbound connection is to your configured LLM provider.

### What's hardened

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

Environment variables for these features are ignored — the values are constants in the source. Each change is marked with a `HARDENED BUILD` comment explaining what was changed and how to revert.

### Prerequisites

- **Bun 1.3+** — a JavaScript/TypeScript runtime (like Node.js). MIT licensed, single binary, no background services or telemetry.
  - macOS/Linux: `curl -fsSL https://bun.sh/install | bash`
  - Windows: `powershell -c "irm bun.sh/install.ps1 | iex"`
  - **Windows AVD / restricted environments:** `npm install -g bun` (avoids curl/domain issues, uses Node.js's OpenSSL which bypasses schannel restrictions)
- **Git**
- **ripgrep** — must be pre-installed on PATH (hardened build won't download it)
  - Windows: `scoop install ripgrep` or `choco install ripgrep` or `npm install -g @vscode/ripgrep`
  - macOS: `brew install ripgrep`
  - Linux: `apt install ripgrep` or `dnf install ripgrep`

### Clone and Build

```bash
# Clone the hardened fork
git clone -b hardened/federal-secure https://github.com/jblenman/opencode.git
cd opencode

# Install dependencies
bun install

# Option A: Run directly from source (dev mode)
bun dev

# Option B: Build a standalone binary for your platform
cd packages/opencode
bun run script/build.ts --single
# Binary output: dist/opencode-{platform}-{arch}/bin/opencode[.exe]
```

### Install the Binary

After building with `--single`, copy the binary to your PATH:

```bash
# macOS/Linux
cp packages/opencode/dist/opencode-darwin-arm64/bin/opencode /usr/local/bin/opencode-patched

# Windows (from Git Bash or PowerShell)
cp packages/opencode/dist/opencode-windows-x64/bin/opencode.exe $HOME/bin/opencode-patched.exe
# Or add the dist directory to your PATH
```

Use `opencode-patched` to avoid conflicting with an existing npm install of `opencode`.

### Windows AVD Quick Start

If you're on a government AVD with Node.js/npm already available:

```powershell
# 1. Install Bun via npm (bypasses curl/schannel issues)
npm install -g bun

# 2. Ensure ripgrep is installed
scoop install ripgrep   # or: choco install ripgrep

# 3. Clone and build
git clone -b hardened/federal-secure https://github.com/jblenman/opencode.git
cd opencode
bun install

# 4a. Run directly from source
bun dev

# 4b. Or build a standalone binary
cd packages/opencode
bun run script/build.ts --single
# Copy dist/opencode-windows-x64/bin/opencode.exe to your PATH
```

No security environment variables needed — they're baked into the source.

**Note:** The `bun install` step pulls packages from `registry.npmjs.org`, which should be accessible on the AVD (Node.js uses OpenSSL, not schannel). If `github.com/jblenman/opencode` is blocked by the keyword firewall, try cloning via SSH or ask your team to whitelist it — the repo name shouldn't trigger content categorization filters.

### Staying Up to Date

```bash
cd opencode

# Pull latest changes from the hardened fork
git pull origin hardened/federal-secure

# Rebuild
bun install
cd packages/opencode && bun run script/build.ts --single
```

If the compaction PR (#16959) gets merged upstream, the hardened branch will be rebased to include future upstream changes.

### Compaction Fix Details

Included in both branches. Fixes AGENTS.md/CLAUDE.md instructions being lost after compaction:

1. **Compaction system prompt** — passes project instructions into the compaction LLM call (was `system: []`)
2. **Summary template** — adds "Active Project Instructions" section to capture behavioral rules
3. **Post-compaction injection** — injects instructions as a `<system-reminder>` message after compaction

---

## Known Issues (March 2026)

- **Codex models** (`gpt-5.3-codex`) don't work via `@ai-sdk/azure` — requires Responses API, which isn't supported yet. Use `gpt-5.2`. Track [issue #13999](https://github.com/sst/opencode/issues/13999).
- **Instruction loss during compaction** — AGENTS.md rules are lost after compaction because the compaction summarizer runs with an empty system prompt. Fix: [PR #16959](https://github.com/anomalyco/opencode/pull/16959), included in both fork branches (see Building from Source above).
- **`openai-compatible` provider** causes "Resource not found" on Azure — always use `@ai-sdk/azure`.
- **Anthropic OAuth** was removed in early 2026 — Claude requires a direct API key, not a Pro/Max subscription.
