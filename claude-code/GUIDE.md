# Claude Code — Configuration Guide

Reference for `CLAUDE.md` and `settings.json`, with reasoning behind each choice and alternatives.

## Installation

```bash
mkdir -p ~/.claude
curl -o ~/.claude/CLAUDE.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/claude-code/CLAUDE.md
curl -o ~/.claude/settings.json https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/claude-code/settings.json
```

---

## File Locations

| File | Scope | Purpose |
|------|-------|---------|
| `~/.claude/CLAUDE.md` | Global — all sessions | Persistent instructions and preferences |
| `~/.claude/settings.json` | Global — all sessions | Tool permissions |
| `<project>/.claude/CLAUDE.md` | Project — that repo only | Project context, conventions, commands |
| `<project>/.claude/settings.json` | Project — shared via git | Project-level permissions |
| `<project>/.claude/settings.local.json` | Project — gitignored | Personal project overrides |

Claude Code loads all applicable CLAUDE.md files (global + project) and merges them. Project files layer on top of global.

---

## CLAUDE.md Reference

CLAUDE.md is loaded into the context window at the start of every session and re-injected after context compaction — so instructions are never silently lost.

**Keep it concise.** Everything in CLAUDE.md costs tokens every session. Put detailed project context in project-level CLAUDE.md files, not the global one.

### Workflow section

The explore-before-acting workflow prevents the most common failure mode: Claude making changes based on incomplete understanding of existing code. The numbered steps give a concrete sequence rather than a vague principle.

**Plan mode** (`shift+tab` in the TUI) switches Claude to a read-only exploration mode before implementing. Use it for anything non-trivial.

### Communication section

Claude's default communication style is already good, but "state assumptions rather than ask for clarification on minor ambiguities" significantly reduces friction. Claude will ask permission for things that don't need it unless told otherwise.

### Code Quality section

These rules prevent the most common over-engineering patterns:
- **Don't add unrequested improvements** — a bug fix should fix the bug, not refactor surrounding code
- **No comments on unchanged code** — avoids cluttering diffs with annotation noise
- **No backwards-compatibility shims** — if you're changing something, change it; don't leave ghost code
- **Prefer editing over creating** — prevents file sprawl

### Git Safety section

The rules use a developer-instinct framing rather than explicit prohibitions. The key insight: telling a model "never commit .claude/" leads to it obsessively caveating "and not the .claude folder" on every response. Instead, framing it as "treat .claude/ like .vs/ — would you think twice about committing .vs?" gets the model to internalize the principle rather than mechanically follow a rule. Claude already has good judgment here; the section mainly prevents edge cases.

### Session Context section

`~/.claude/session-context.md` is the continuity mechanism. Claude Code compacts context automatically but can be `/clear`ed, and sessions can be interrupted. The context file lets a new session pick up where the last one left off without re-explaining everything.

Update it frequently during long tasks — not just at the end.

---

## settings.json Reference

### Permission model

Claude Code uses a deny-first model: everything not explicitly allowed is denied (or prompts). The evaluation order is: **deny > allow > prompt**.

```json
{
  "permissions": {
    "allow": ["Tool(specifier)"],
    "deny": ["Tool(specifier)"]
  }
}
```

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
| `Task` | Subagent type | `Task(*)`, `Task(Explore)` |
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
- `Bash(*)` allows all shell commands — use this for a trusted global config where you don't want permission prompts
- The old `Bash(command:*)` colon syntax is deprecated — use a space: `Bash(git *)` not `Bash(git:*)`

### Tightening permissions

The template uses broad permissions (`Bash(*)`, etc.) for a personal global config where friction is unwanted. For shared project settings or sensitive environments, narrow them:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit(src/**)",
      "Write(src/**)",
      "Glob",
      "Grep",
      "Bash(git *)",
      "Bash(npm run *)",
      "Bash(npm test *)"
    ],
    "deny": [
      "Bash(rm *)",
      "Bash(curl *)"
    ]
  }
}
```

---

## Memory System

Claude Code maintains auto-memory files at:
```
~/.claude/projects/<project-hash>/memory/MEMORY.md
```

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
            "command": "python3 /path/to/script.py",
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
- Exit code `2` blocks the action; exit `0` allows it
- `UserPromptSubmit` fires on every message — use a cooldown to avoid overhead

---

## Image Context Warning

Reading images with the Read tool puts them into the conversation context. This has hard limits:

- **Per image:** Cannot exceed ~2000×2000 pixels
- **Cumulative:** Total image data across a session can cause an **unrecoverable** API error — `/compact` won't fix it, only `/clear` will (which wipes all session context)

**Safe pattern:** Use a Task subagent to read images instead of reading them directly. The subagent sees the image, returns a text description, and the image never enters the main context.

```
Task(
  prompt="Read the image at /tmp/shot.png and describe what you see in detail.",
  subagent_type="general-purpose"
)
```

---

## Key Differences from Codex CLI / OpenCode

| | Claude Code | Codex CLI | OpenCode |
|---|---|---|---|
| Model | Claude (Opus/Sonnet) | GPT (OpenAI only) | Any provider |
| Reasoning quality | Excellent natively | Needs coaching | Needs coaching |
| Context management | Re-injects CLAUDE.md after compaction | Real compaction via Responses API | LLM-based compaction — system prompt rebuilt each loop, but conversational context can drift |
| Instruction file | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` + `CLAUDE.md` (reads both) |
| Config file | `settings.json` | `config.toml` | `opencode.json` |
| Sub-agents | Built-in (Task tool) | `multi_agent` feature | Custom agents (primary + subagent) |
| Undo | No | `undo` feature (git snapshots) | `/undo` (git snapshots) |

Claude Code requires the least coaching because Claude (especially Opus) already explores alternatives, self-corrects, and pushes back on bad assumptions. The CLAUDE.md here focuses on workflow preferences and code quality rules rather than compensating for reasoning deficiencies.
