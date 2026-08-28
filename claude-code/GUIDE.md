# Claude Code — Configuration Guide

Reference for `CLAUDE.md` and `settings.json`, with reasoning behind each choice and alternatives. For an isolated / Bedrock environment, see [`profiles/bedrock-gov/SETUP.md`](profiles/bedrock-gov/SETUP.md).

## Installation

From a clone of this repo (it's private, so raw GitHub URLs need a token — cloning is simpler):

```powershell
$src = "$HOME\ai-agent-templates\claude-code"
New-Item -ItemType Directory -Path "$HOME\.claude" -Force
Copy-Item "$src\CLAUDE.md"     "$HOME\.claude\CLAUDE.md"
Copy-Item "$src\settings.json" "$HOME\.claude\settings.json"
```

Both files are self-contained, so they can also be transferred by hand into an environment with no repo access.

---

## File Locations

| File | Scope | Purpose |
|------|-------|---------|
| `~/.claude/CLAUDE.md` | Global — all sessions | Persistent instructions and preferences |
| `~/.claude/settings.json` | Global — all sessions | Permissions, model, env vars |
| `<project>/.claude/CLAUDE.md` | Project — that repo only | Project context, conventions, commands |
| `<project>/.claude/settings.json` | Project — shared via git | Project-level permissions (not `defaultMode: auto` — that only works from the user file) |
| `<project>/.claude/settings.local.json` | Project — gitignored | Personal project overrides |
| `managed-settings.json` (OS-level path) | Machine — set by an administrator | Locked policy; outranks user settings |

Claude Code loads all applicable CLAUDE.md files (global + project) and merges them. Project files layer on top of global.

---

## CLAUDE.md Reference

CLAUDE.md is loaded into the context window at the start of every session and re-injected after context compaction — so instructions are never silently lost.

**Keep it concise.** Everything in CLAUDE.md costs tokens every session. Put detailed project context in project-level CLAUDE.md files, not the global one.

**Written for Opus 5-class models.** Anthropic's migration guidance for Opus 5 (and the prompt-audit guidance for current models generally) changed what a good instruction file looks like: current models plan, explore, and verify their own work without being told, and step-by-step choreography ("1. read, 2. state your plan, 3. implement, 4. verify") now causes over-planning and worse output. What Opus 5 *does* need is told explicitly: keep responses concise (its default is longer than earlier models'), stay inside the requested scope (it expands scope readily), and communicate outcome-first. The file therefore states goals and constraints and leaves the method to the model.

### Workflow section

"Understand before changing" and "surface scope growth" are the two constraints that still earn their place. The old numbered steps are gone on purpose — don't add them back. Plan mode (`shift+tab`) is still useful, but it's a choice *you* make per task, not an instruction the model needs.

### Communication section

Outcome-first, brief, assumptions stated — the Opus 5 conciseness instruction, plus the "plain register" rule: findings are stated with their evidence strength (confirmed / likely / possible), never dressed up as a detective story. Dramatic framing signals more confidence than the evidence supports.

### Accuracy section

Four habits that prevent the expensive class of mistakes:
- **Verified vs recalled.** Anything that drifts (versions, APIs, product behavior) gets checked at the source when the user will act on it; if it can't be checked, the answer says so.
- **Hard identifiers before acting.** A name/location/timing coincidence is a hypothesis. Before editing, deleting, sending, or citing on the strength of one, confirm an exact filename, ID, hash, path, or verbatim error text — and treat a failed check as disconfirmation. This failure mode gets worse near the end of a long session, so the rule says to lean on it hardest there.
- **Evidence in reports.** Concrete test/command output, not "it should work"; subtle risks flagged proactively. Agentic workflows train people to read less of the code, so the report has to carry the proof.
- **Incremental ordinal search.** "Most recent N" is scanned in order in small batches with early stop — never a wide pre-scan.

### Code Quality section

The over-engineering guards (no unrequested improvements, no comments on unchanged code, no compat shims, edit over create) plus two additions: comment the *why* in non-trivial new code (the reviewer reads diffs), and match the surrounding code's idiom. "Keep builds warning-clean" is a standing build policy.

### Destructive and Irreversible Actions section

Confirm before anything lossy or outward-facing, look before overwriting, and prefer the minimal reversible action (`git rm --cached` over a history rewrite, untrack + ignore over a scrub, move over delete). Destructive options are offered as optional when warranted, never as the default.

### Git Safety section

The rules use a developer-instinct framing rather than explicit prohibitions. Telling a model "never commit .claude/" leads to it obsessively caveating "and not the .claude folder" on every response; framing it as "treat .claude/ like .vs/ — would you think twice about committing .vs?" gets the principle internalized. Claude already has good judgment here; the section mainly prevents edge cases.

### Session Context section

`~/.claude/session-context.md` is the continuity mechanism. Claude Code compacts context automatically but can be `/clear`ed, and sessions can be interrupted. The section now also says *what* to write first — decisions with reasons, user corrections, exact identifiers, open questions — because those are the things that exist only in conversation and vanish at compaction. Completed work is already in files.

### Images section

Images read with the Read tool land in the main context (see Image Context Warning below). The rule routes them through a subagent that returns text.

---

## settings.json Reference

### Permission model

Modes set the baseline; rules layer on top. Evaluation order: **deny > ask > allow > mode default**. Deny rules block in every mode, including `bypassPermissions`, and apply to subagents.

```json
{
  "permissions": {
    "defaultMode": "auto",
    "allow": ["Tool(specifier)"],
    "deny": ["Tool(specifier)"]
  }
}
```

### Why `defaultMode: "auto"` with a read-only allow list

The template's stance: **read anything without prompts; confirm before destructive or irreversible actions.** Auto mode does that — a separate classifier model reviews each action that isn't covered by a rule: routine work is allowed silently, destructive or out-of-scope actions prompt, and hostile-content-driven actions are blocked. Explicit `ask` rules still prompt.

Two consequences shape the allow list:

- **Allow rules bypass the classifier.** A tool in `allow` is never reviewed, so `allow` should hold only tools that can't lose data: `Read`, `Glob`, `Grep`, `WebSearch`, `WebFetch`, `Agent`, `Skill`. `Edit`, `Write`, `Bash`, and `NotebookEdit` are intentionally absent so the classifier sees them.
- **Auto mode drops broad code-execution allows on entry** — blanket `Bash(*)` / `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and whole-tool `Agent` and `Monitor` rules — and restores them when you leave the mode. Narrow rules like `Bash(npm test *)` stay in effect. So `Bash(*)` in `allow` under auto mode buys nothing and removes the guard everywhere else.

Claude Code also auto-records narrow `Bash(...)` / `Edit(...)` rules as you approve things. Trim them occasionally; they pile up and can quietly re-broaden access.

Auto mode needs a supported model (Opus 4.6+ / Sonnet 4.6+ / Fable 5 on the Anthropic API; Sonnet 5 / Opus 4.7+ / Fable 5 on Bedrock, Vertex Agent Platform, and Foundry). When it isn't available the session starts in Manual mode — safe, just more prompts.

Other `defaultMode` values: `default` (Manual — reads only), `acceptEdits` (edits and common filesystem commands without prompts), `plan` (read-only exploration), `dontAsk` (only pre-approved tools; locked-down scripts), `bypassPermissions` (everything; isolated containers only).

### Tool permission patterns

| Tool | Pattern | Example |
|------|---------|---------|
| `Read` | Path glob (optional) | `Read`, `Read(.claude/**)` |
| `Edit` | Path glob (optional) | `Edit`, `Edit(src/**)` |
| `Write` | Path glob (optional) | `Write` |
| `Glob` | No specifier | `Glob` |
| `Grep` | No specifier | `Grep` |
| `Bash` | Command prefix + wildcard | `Bash(git *)`, `Bash(npm run *)` |
| `WebFetch` | Domain filter (optional) | `WebFetch`, `WebFetch(domain:github.com)` |
| `WebSearch` | No specifier | `WebSearch` |
| `Agent` | Subagent type | `Agent`, `Agent(Explore)` — older configs called this tool `Task` |
| `NotebookEdit` | No specifier | `NotebookEdit` |
| `MCP` | `server__tool` format | `mcp__puppeteer__puppeteer_navigate` |

### Path prefix rules (Read/Edit/Write)

| Prefix | Resolves relative to |
|--------|---------------------|
| `/path` | Location of the settings file |
| `~/path` | Home directory |
| `//path` | Absolute filesystem path |
| `path` or `./path` | Current working directory |
| `**` | Recursive wildcard |

### Bash pattern notes

- `Bash(npm run *)` — the space before `*` enforces a word boundary. Without it, `Bash(npm*)` would also match `npmx`, `npm-check`, etc.
- Current docs show both the space form (`Bash(git push *)`) and the colon form (`Bash(curl:*)`); this template uses the space form.
- Scoped allows are the way to cut prompt friction without losing the guard: `Edit(~/notes/**)`, `Bash(git status *)`, `Bash(npm test *)`.

### Other settings used by the templates

| Setting | Purpose |
|---------|---------|
| `effortLevel` | Persisted effort (`low`–`xhigh`; `max` is session-only via `/effort max`). `xhigh` is Claude Code's coding default; pinning it prevents a silent downgrade. |
| `model` | Default model or alias (`opus`, `sonnet`); on Bedrock the alias resolves through `ANTHROPIC_DEFAULT_OPUS_MODEL` etc. |
| `env` | Environment variables applied to every session — the right place for provider switches and kill-switches you don't want leaking to other processes. |
| `attribution` | Commit/PR attribution: `commit`, `pr`, `sessionUrl` (each `false` to omit). Replaces the deprecated `includeCoAuthoredBy`. |
| `autoMemoryDirectory` | Move auto-memory out of the per-project default (`~/.claude/projects/<hash>/memory/`) to a shared location. |
| `remoteControlAtStartup` | Start Remote Control (phone/web takeover through claude.ai) each session. Needs a claude.ai login; keep `false` anywhere that must not reach claude.ai. |
| `enableWorkflows` | Exposes the multi-agent Workflow tool. Capability only; nothing spawns unless asked. |
| `enableAllProjectMcpServers` / `enabledMcpjsonServers` / `disabledMcpjsonServers` | Approve, allow-list, or block MCP servers declared in project `.mcp.json` files. |
| `skipWebFetchPreflight` | Skip the hostname safety check WebFetch normally sends to `api.anthropic.com`. |
| `awsAuthRefresh` / `awsCredentialExport` | Bedrock credential refresh hooks (see the Bedrock profile). |

### Restricted environments

For an environment that must not reach the public internet or leak internal data, use [`profiles/bedrock-gov/`](profiles/bedrock-gov/): Bedrock provider, `WebFetch`/`WebSearch` denied outright, all non-essential traffic off, and a CLAUDE.md "Environment" section that tells the model the boundary rules. An administrator can pin the same `permissions` block in managed settings so users can't loosen it.

---

## Memory System

Claude Code maintains auto-memory files at:
```
~/.claude/projects/<project-hash>/memory/MEMORY.md
```
(or wherever `autoMemoryDirectory` points — one shared memory for all projects when set).

The first 200 lines of `MEMORY.md` are automatically loaded into the system prompt. Use it for stable patterns and preferences that emerge from working on a project.

**What to save:**
- Stable patterns and conventions confirmed across multiple sessions
- Key architectural decisions and important file paths
- Solutions to recurring problems
- User preferences for workflow and tools

**What not to save:**
- Session-specific state (use `session-context.md` for that)
- Speculative or unverified conclusions
- Anything that duplicates CLAUDE.md
- Secrets, and in a restricted environment, internal identifiers that don't need to be there

For detailed notes, create separate topic files and link to them from MEMORY.md. Lines past 200 in MEMORY.md are truncated.

---

## Hooks

Claude Code hooks let scripts run at lifecycle events, injecting context or blocking actions.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "py /path/to/script.py || exit 1",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### Hook events

| Event | When | Can inject context | Can block |
|-------|------|--------------------|-----------|
| `SessionStart` | Session starts/resumes | Yes | No |
| `UserPromptSubmit` | User sends a prompt | Yes (stdout) | Yes (exit 2) |
| `PreToolUse` | Before tool call | Yes | Yes (exit 2) |
| `PostToolUse` | After tool call | Yes | No |
| `Notification` | System notifications | Yes | No |
| `Stop` | Claude finishes responding | No | Yes |

- Stdout from hook commands is injected into the conversation as context
- Exit code `2` blocks the action; exit `0` allows it; any other non-zero code is a non-blocking error
- **Always end a hook command with `|| exit 1`.** A hook that fails with exit 2 — which is what an interpreter that can't find its script or is denied file access tends to produce — blocks every prompt and locks the session out. `|| exit 1` turns any failure into a logged, non-blocking error.
- Call interpreters by launcher (`py`, `python3`), not a hard-coded install path; hard-coded paths break on the next runtime upgrade
- `UserPromptSubmit` fires on every message — use a cooldown to avoid overhead

---

## Image Context Warning

Reading images with the Read tool puts them into the conversation context. This has hard limits:

- **Per image:** Cannot exceed ~2000×2000 pixels
- **Cumulative:** Total image data across a session can cause an **unrecoverable** API error — `/compact` won't fix it, only `/clear` will (which wipes all session context)

**Safe pattern:** Use a subagent to read images instead of reading them directly. The subagent sees the image, returns a text description, and the image never enters the main context. Capture screenshots at ~1800px max width — smaller is hard to read, 2000+ risks the limit.

```
Agent(
  prompt="Read the image at C:/temp/shot.png and describe what you see in detail.",
  subagent_type="general-purpose"
)
```

---

## Key Differences from Codex CLI / OpenCode

| | Claude Code | Codex CLI | OpenCode |
|---|---|---|---|
| Model | Claude (Opus 5 / Sonnet 5 / Fable 5) via Anthropic API, Bedrock, Vertex, or Foundry | GPT (OpenAI only) | Any provider |
| Reasoning quality | Excellent natively | Needs coaching | Needs coaching |
| Context management | 1M window on current models; re-injects CLAUDE.md after compaction | Real compaction via Responses API | LLM-based compaction — system prompt rebuilt each loop, but conversational context can drift |
| Instruction file | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` + `CLAUDE.md` (reads both) |
| Config file | `settings.json` | `config.toml` | `opencode.json` |
| Sub-agents | Built-in (Agent tool) | `multi_agent` feature | Custom agents (primary + subagent) |
| Undo | No | `undo` feature (git snapshots) | `/undo` (git snapshots) |

Claude Code requires the least coaching because Claude (especially Opus) already explores alternatives, self-corrects, and pushes back on bad assumptions. The CLAUDE.md here focuses on outcomes, constraints, and accuracy habits rather than compensating for reasoning deficiencies.
