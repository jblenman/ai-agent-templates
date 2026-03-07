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

**Context truncation warning** — OpenCode deletes the oldest messages when the context window fills, with no compression. This file's instructions can be silently lost mid-session. The Session Management section addresses this directly.

**Plan mode** — OpenCode's plan mode is activated with **Tab** in the composer. This switches to a read-only exploration mode where the model can look at files without making changes. Use it before any non-trivial implementation. The Codex equivalent is prompting explicitly ("explore only, don't make changes yet").

**`/compact`** — OpenCode's manual compaction command. Run it proactively when the context window starts getting full. Don't wait for auto-truncation, which drops your earliest context (including these instructions) first.

### Session management strategy

The context truncation problem fundamentally changes how you should work with OpenCode compared to Codex:

1. **Keep sessions shorter.** Treat sessions as disposable. Start fresh often.
2. **Session context file is your continuity.** Not a nice-to-have — it's how you carry context between sessions without relying on conversation history that will be truncated.
3. **Restart, don't rescue.** When behavior degrades (shallow responses, ignoring git rules, losing project context), starting a fresh session with your context notes is dramatically more effective than trying to re-inject instructions into a degraded session drowning in stale context.
4. **Watch the token counter.** When usage is high, wrap up or start fresh.
5. **Verify periodically.** Ask "repeat back your core instructions from AGENTS.md" to confirm instructions haven't been truncated.

### Reasoning coaching

The same coaching as the Codex AGENTS.md applies. GPT-5.2 gives the first plausible answer without self-correcting unless specifically instructed not to. The explicit "2 alternatives" and "question assumptions" requirements directly counter this. Vague instructions ("think carefully") are less effective than specific requirements.

OpenCode also supports an `AGENTS.md` reasoning section. Plan mode (Tab) provides a natural "think first" phase — use it before any implementation.

---

## Known Issues (March 2026)

- **Codex models** (`gpt-5.3-codex`) don't work via `@ai-sdk/azure` — requires Responses API, which isn't supported yet. Use `gpt-5.2`. Track [issue #13999](https://github.com/sst/opencode/issues/13999).
- **Context truncation** is the biggest operational issue with OpenCode. See Session Management above.
- **`openai-compatible` provider** causes "Resource not found" on Azure — always use `@ai-sdk/azure`.
- **Anthropic OAuth** was removed in early 2026 — Claude requires a direct API key, not a Pro/Max subscription.
