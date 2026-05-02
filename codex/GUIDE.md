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

### Model & Reasoning (GPT-5.5 tuning)

**`model = "gpt-5.5"`**
The current default. GPT-5.5 (April 2026) is more efficient at reasoning than 5.4 and benefits from short, outcome-first prompts rather than process-heavy coaching. **Pricing cliff:** OpenAI charges 2× input and 1.5× output for the entire request once a single prompt crosses 272K input tokens. Stay below the cliff with `model_auto_compact_token_limit = 270000`.

**`model_reasoning_effort = "medium"`**
Per OpenAI's Codex prompting guide, `"medium"` is the explicit recommendation for interactive coding with GPT-5.5. **Higher effort can regress quality** when stopping criteria are weak or tools are open-ended ("overthinking, unnecessary searching, or output quality regressions" — quoted from the guidance). This is a behavior change from 5.2/5.4 where `xhigh` was the right default.
- `"low"` for tool-loop / multi-step decisions where speed matters
- `"high"` only when evals show it produces measurable wins on hard tasks
- `"xhigh"` reserved for the absolute hardest tasks; rarely justified
- Live-tune in TUI with `Alt+,` (lower) / `Alt+.` (higher) on Codex v0.124.0+

**`model_reasoning_summary = "auto"`**
GPT-5.5 is concise by default — forcing `"detailed"` adds noise without helping much. `"auto"` lets the model decide.
- `"detailed"` for the `deep` profile when you want to audit reasoning
- `"none"` to hide reasoning entirely

**`model_verbosity = "low"`**
Per OpenAI's prompt guidance, `"low"` is a better starting point than the API default of `"medium"` for coding agents. The model already defaults to "more concise and direct" output on 5.5 — explicit `"low"` reinforces that.
- `"medium"` for customer-facing prose where polish matters

**`personality = "pragmatic"`**
Direct, no fluff. Requires `features.personality = true`.
- `"friendly"` for warmer tone, useful for onboarding/ambiguous tasks per OpenAI's guidance
- `"none"` for model default

**`plan_mode_reasoning_effort = "high"`**
Separate reasoning level for the plan/explore phase. `"high"` rather than `"xhigh"` — planning shouldn't burn maximum reasoning when implementation does the real work.

**`review_model = "gpt-5-mini"`**
The model used by `/review`. Code review doesn't need the same depth as implementation, so a faster/cheaper model is fine.
- Change to your primary model if you want top-quality reviews

---

### Context

**`model_auto_compact_token_limit = 270000`** (NEW for GPT-5.5)
Triggers compaction at 270K input tokens, just under OpenAI's 272K pricing cliff. Once a single prompt crosses 272K, the entire request is billed at 2× input / 1.5× output for that turn — including the 270K of conversation already there. Compacting earlier avoids the surcharge.
- Raise to ~900000 if you genuinely need long-context retrieval and accept the cost
- Set to `-1` to disable auto-compaction entirely (let context fill to limit)

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

**`approval_policy = "untrusted"`**
Controls when Codex asks for permission before running commands.
- `"untrusted"` — auto-approves known safe read-only commands; still prompts for anything that writes or executes. Best default: reads never interrupt you, destructive ops still require approval
- `"on-request"` — model decides when to ask. Tends to ask constantly, even for reads
- `"never"` — never asks; failures are returned to the model. Use for fully trusted sessions or the `fast` profile

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

**`web_search = "disabled"`**
Default for Azure deployments — most Azure orgs reject `web_search_preview` ("Tool 'web_search_preview' disabled for this organization"), and a misplaced `web_search` key (after any `[table]` header) is silently ignored, leaving you stuck with that error.
- `"cached"` for non-Azure setups — routes through OpenAI's API, uses cached results
- `"live"` for always-fresh results (non-Azure)
- **Must be a root-level key** (above any `[table]` header) or it's silently ignored — this is the most common config bug in Codex

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

**`[profiles.fast]`** — `gpt-5-mini` with `low` reasoning, no approval prompts. Good for quick iterations on straightforward tasks (triage, file extraction, transforms).
**`[profiles.deep]`** — `gpt-5.5-pro` with `high` reasoning and detailed summaries. For hard design/audit work where Pro tier earns its cost. **Note:** `"xhigh"` is no longer the default for the deep profile — per OpenAI's guidance, escalating beyond `high` rarely produces measurable wins and can regress quality. Promote to `xhigh` only with eval evidence.

You can add more profiles for specific contexts (e.g., a `review` profile that uses a different model).

---

## TUI Reasoning Hotkeys (Codex v0.124.0+)

- `Alt+,` — lower reasoning effort one step
- `Alt+.` — raise reasoning effort one step
- Switching models resets reasoning to the new model's default rather than preserving your last setting

---

## AGENTS.md Reference

The coaching file loaded at session start. Codex auto-discovers `AGENTS.md` files from repo root down to the working directory, with later directories overriding earlier ones; the model has been trained to closely adhere to these injected instructions.

### Why this AGENTS.md is short

Tuned for **GPT-5.5**. OpenAI's prompt guidance for 5.5 explicitly inverts the playbook from earlier models: "Shorter, outcome-first prompts usually work better than process-heavy prompt stacks." Long "think step-by-step / consider 2 alternatives / explore before acting" coaching that helped 5.2/5.4 now causes 5.5 to over-process or stop early during rollouts ("can cause the model to stop abruptly before the rollout is complete" — quoted from Codex prompting guide).

For older models (5.1/5.2 deployments), the GPT-5.1 profile keeps the heavier coaching that those weaker models still benefit from.

### Key sections and why they're worded the way they are

**Role / Goal / Success Criteria** — Defines the destination, not the path. Lets the model choose the most efficient route. Per OpenAI: "describe what good looks like, what constraints matter, what evidence is available, and what the final answer should contain."

**Constraints** — Tool preferences and code-quality rules that genuinely apply across tasks. Things like "prefer `apply_patch` over shell" matter because the model was trained specifically on `apply_patch`.

**Output** — Explicit `verbosity: low`, no upfront-plan/preamble requirement, hard floor on update cadence. The "no preamble" guidance is critical: Codex prompting guide explicitly warns that prompting for status updates "can cause the model to stop abruptly before the rollout is complete."

**Stop Rules** — How to know when to bail out. "Don't end the turn with only a plan" comes directly from the official Codex prompt: "Unless asked for a plan, never end the interaction with only a plan."

**Git Safety** — Uses a developer-instinct framing rather than explicit prohibitions. From a real incident where GPT force-pushed `.gitignore`d files: telling a model "never commit .claude/" leads to it obsessively caveating "and not the .claude folder" on every response. Framing it as "treat .claude/ like .vs/ — would you think twice about committing .vs?" gets the model to internalize the principle. Concrete guardrails (no force-push, always check `git status`) still included but lead with the intuition.

**Session Continuity** — Codex's server-side encrypted compaction (OpenAI provider) preserves instructions reliably. No instruction-loss issue like OpenCode pre-fix. The session context file is still useful for resuming across sessions.

---

## Recent Codex CLI Updates (Apr 2026)

| Version | Date | Highlights |
|---|---|---|
| v0.128.0 | Apr 30 | **GPT-5.5 support** (bundled OpenAI Docs skill updated). Persisted `/goal` workflows. Expanded permission profiles. MultiAgentV2 thread caps |
| v0.125.0 | Apr 24 | App-server Unix socket transport. Permission profiles round-trip across TUI/MCP/app-server. `codex exec --json` reports reasoning-token usage |
| v0.124.0 | Apr 23 | **TUI quick reasoning controls: `Alt+,` lower / `Alt+.` raise.** Model upgrades reset reasoning to new model's default. First-class Bedrock support. Hooks now stable in `config.toml` |

## Per-project Setup

Add a `.codex/config.toml` at the repo root to override settings for that project:

```toml
# .codex/config.toml
model = "gpt-5.5-pro"            # use Pro tier for hard design/audit work
# or: model = "gpt-5.3-codex"    # for Codex-trained model on Azure
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
