# Codex CLI — Configuration Guide

Reference for `config.toml` and `AGENTS.md` settings, with reasoning behind each choice and alternatives.

## Installation

```bash
mkdir -p ~/.codex
curl -o ~/.codex/config.toml https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/codex/config.toml
curl -o ~/.codex/AGENTS.md https://raw.githubusercontent.com/jblenman/ai-agent-templates/main/codex/AGENTS.md
```

For project-specific instructions, add an `AGENTS.md` or `.claude/CLAUDE.md` at the repo root.

---

## config.toml Reference

### Model & Reasoning

**`model_reasoning_effort = "xhigh"`**
Controls how hard the model thinks before responding. The most impactful single setting for GPT quality.
- `"high"` is a reasonable alternative if you find `"xhigh"` noticeably slower on simple tasks
- `"medium"` for quick/throwaway sessions — use the `fast` profile instead (see Profiles)
- This is the primary lever for getting Claude-like exploration and self-correction out of GPT

**`model_reasoning_summary = "detailed"`**
Shows the model's reasoning steps in the output. Useful for understanding why it made a choice and catching bad reasoning early.
- `"concise"` if you want a brief summary without the full chain
- `"none"` to hide reasoning entirely (faster output, less transparency)
- `"auto"` lets the model decide

**`model_verbosity = "high"`**
Controls response detail level. `"high"` produces thorough explanations.
- `"medium"` if responses feel too verbose for your workflow
- Has less impact than `model_reasoning_effort`

**`personality = "pragmatic"`**
Sets communication style. `"pragmatic"` is direct and skips filler language. Requires `features.personality = true`.
- `"friendly"` if you prefer a warmer tone
- `"none"` to use the model's default

**`plan_mode_reasoning_effort = "high"`**
Separate reasoning level for the plan/explore phase. Kept at `"high"` rather than `"xhigh"` since planning is usually read-only and you don't need maximum depth for exploration — save the heavy thinking for implementation.
- Set to `"xhigh"` if you want maximum analysis during planning too
- Set to `"medium"` to speed up the planning phase

**`review_model = "gpt-5-mini"`**
The model used when you run `/review`. Since code review doesn't require the same depth as implementation, a faster/cheaper model is usually fine here.
- Change to your primary model if you want the same quality for reviews

---

### Context

**`tool_output_token_limit = 32000`**
How many tokens of tool output (file reads, command results) are kept in context. The default is much lower, which causes large files to be truncated before the model can fully read them.
- Increase further if you work with very large files or codebases
- Decrease if you're hitting cost limits and can accept more truncation

**`project_doc_max_bytes = 65536`**
How much of your `AGENTS.md` to read (64KB). The default is smaller — if your coaching file is long, it may be silently truncated.
- Increase to `131072` (128KB) if your AGENTS.md files are large
- The file is read at session start, so this only matters if you have extensive instructions

**`project_doc_fallback_filenames = [".claude/CLAUDE.md", "CLAUDE.md"]`**
If no `AGENTS.md` exists in a project, Codex checks these filenames instead. This lets you share a single instruction file across Claude Code and Codex CLI without duplication.
- Add `"CODEX.md"` or other names if you use different conventions
- Remove if you want to maintain separate files per tool

---

### Approval & Sandbox

**`approval_policy = "on-request"`**
Controls when Codex asks for permission before running commands.
- `"on-request"` — model decides when to ask. Significantly less friction than the default without being fully autonomous
- `"never"` — never asks; failures are returned to the model. Use for fully trusted environments or combine with `--full-auto`
- `"untrusted"` — auto-approves known safe read-only commands; asks for anything that writes or executes

**`sandbox_mode = "workspace-write"`**
Controls what Codex can access on the filesystem.
- `"workspace-write"` — can read anywhere, write within the project directory. Good default balance
- `"danger-full-access"` — unrestricted filesystem access. Use per-project in `.codex/config.toml` for trusted repos, or via `codex --yolo` for a single session
- `"read-only"` — can only read; useful for pure exploration or review tasks

> **Session-level overrides:**
> - `codex --full-auto` — workspace-write + on-request approvals, no config change needed
> - `codex --yolo` — bypasses all approvals and sandbox for the session

---

### Outbound Privacy

**`check_for_update_on_startup = false`**
Disables the npm registry check at startup. The check itself only sends your platform/version info (no personal data), but unnecessary outbound calls are unnecessary.

**`web_search = "cached"`**
Web search routes through the OpenAI API — your machine never connects directly to a search engine. `"cached"` uses previously fetched results where available.
- `"live"` for always-fresh results
- `"disabled"` to turn it off entirely if you don't want search capability

**`[analytics] enabled = false` / `[feedback] enabled = false`**
Disables OpenAI usage analytics and feedback collection. Neither sends sensitive data, but there's no reason to have them on.

---

### Local History & Memory

**`[history] persistence = "save-all"`**
Saves all session history to `~/.codex/history.jsonl`. Useful for going back to find things the model has forgotten or to audit what it did.
- `"none"` if you explicitly don't want sessions written to disk
- `max_bytes = 209715200` caps the file at 200MB before old entries are pruned

**`[memories]`**
Cross-session memory subsystem. Generates summaries of sessions and injects them at startup, giving the model continuity across sessions — partially compensating for GPT's lack of long-term memory.
- Requires `features.memories = true`
- `min_rollout_idle_hours = 6` — memories are generated after 6 hours of idle time. The default is 12h; 6h gives faster consolidation
- `no_memories_if_mcp_or_web_search = false` — still generate memories even in sessions that used MCP tools or web search (the default is `true`, which skips memory generation for these sessions)
- `max_raw_memories_for_consolidation = 512` — how many raw memories to keep before consolidating. Higher = more context but slower consolidation

---

### Features

**`undo = true`**
Creates a git snapshot before each change, enabling `codex undo` to roll back. Essential safety net.
- Uses `[ghost_snapshot]` config for tuning (see schema for options)

**`multi_agent = true`**
Enables spawning parallel sub-agents for larger tasks. The model can break work into parallel streams.
- Control thread limits with `[agents] max_threads` and `max_depth`

**`child_agents_md = true`**
**Critical.** Without this, sub-agents do not inherit your AGENTS.md coaching — they start completely unconfigured. Off by default.

**`memories = true`**
Required to enable the `[memories]` subsystem above.

**`prevent_idle_sleep = true`**
Prevents the system from sleeping while Codex is actively running a task. Useful for long overnight jobs.

**`js_repl = true`**
Enables a persistent Node.js REPL the model can use for calculations, data transformation, and scripting tasks without spawning a full shell. Requires Node.js installed.
- Set a per-call timeout with a first-line pragma: `// codex-js-repl: timeout_ms=15000`

**`request_permissions = true`**
Allows the model to request additional filesystem permissions mid-session without fully leaving the sandbox. More flexible than either a hard sandbox or full access.

**`codex_git_commit = true`**
Adds git commit attribution guidance to the model's instructions, encouraging better commit messages and attribution practices.

---

### Shell Environment

**`[shell_environment_policy] inherit = "all"`**
Passes your full shell environment to processes Codex spawns. Useful when your tools depend on env vars (PATH, credentials, etc.).
- `"core"` — only essential platform variables (HOME, PATH, SHELL). Better for security-sensitive environments
- `"none"` — no variables inherited; set only what you explicitly need via `set = { ... }`
- Use `exclude = ["*SECRET*", "*TOKEN*"]` patterns to strip specific vars

---

### TUI

**`status_line`**
Customizes what's shown in the bottom status bar. Available items:
`model-with-reasoning`, `model-name`, `context-remaining`, `context-used`, `context-window-size`, `used-tokens`, `total-input-tokens`, `total-output-tokens`, `git-branch`, `current-dir`, `project-root`, `codex-version`, `session-id`, `five-hour-limit`, `weekly-limit`

**`animations = false`**
Disables the welcome shimmer and spinners. Cleaner, slightly faster startup.

---

### Profiles

Switch profiles with `codex --profile <name>`.

**`[profiles.fast]`** — lower reasoning, no approval prompts. Good for quick iterations on straightforward tasks.
**`[profiles.deep]`** — maximum reasoning with detailed summaries. For hard problems where you want the most careful analysis.

You can add more profiles for specific contexts (e.g., a `review` profile that uses a different model).

---

## AGENTS.md Reference

The coaching file loaded at session start. Codex re-injects this after context compaction, so instructions persist across long sessions (unlike OpenCode).

**Key sections and why they're worded the way they are:**

**Reasoning & Approach** — GPT's default behavior is to give the first plausible answer without exploring alternatives. The explicit instructions to "consider 2 alternatives" and "question assumptions" directly counter this tendency. Vague coaching ("think carefully") is less effective than specific requirements.

**Explore before acting** — The numbered workflow (read → plan → implement → verify) gives the model a concrete sequence to follow rather than a general principle. The note about doing a quick read even when asked to "just do it" protects against the common failure mode of the model making changes based on incomplete understanding.

**Communication** — "State your assumption and proceed" is intentional. Constant clarification requests are friction. The model should make reasonable assumptions explicit and move forward, reserving questions for genuinely consequential decisions.

**Git Safety** — These rules exist because of a real incident where GPT force-pushed a `.gitignore`d `.claude/` folder (containing auth tokens and settings) to a remote repo to literally fulfill "commit and push everything." The model lacked the judgment to distinguish "everything you'd want committed" from "everything on disk." The rules are explicit rather than principle-based because GPT needs concrete guardrails, not abstractions.

**Code Quality** — Mirrors Claude Code's defaults. Prevents the common pattern of the model "improving" surrounding code, adding unnecessary abstractions, or creating files that weren't asked for.

**Session Continuity** — Mainly relevant if you move to a tool with worse context management (like OpenCode). In Codex, context compaction preserves instructions, so these notes are more informational than operational.

---

## Per-project Setup

Add a `.codex/config.toml` at the repo root to override settings for that project:

```toml
# .codex/config.toml
model = "gpt-5.3-codex"          # different model for this project
sandbox_mode = "danger-full-access"
approval_policy = "never"
```

Add an `AGENTS.md` or `.claude/CLAUDE.md` at the repo root with project context:

```markdown
## Project Context
[What this project is and does]

## Tech Stack
[Languages, frameworks, key dependencies]

## Coding Conventions
[Style, naming, patterns to follow/avoid]

## Key Files
[Important files/dirs to know about]

## Commands
- Build: `...`
- Test: `...`
- Lint: `...`
```
