# Codex CLI — Configuration Guide

Reference for `config.toml`, `AGENTS.md`, the hooks, skills and the knowledge-base starter, with the reasoning behind each choice. Checked against the Codex 0.160 config reference on 2026-10-05.

## Installation

```bash
git clone https://github.com/jblenman/ai-agent-templates ~/ai-agent-templates
mkdir -p ~/.codex/hooks
cp ~/ai-agent-templates/codex/config.toml      ~/.codex/config.toml
cp ~/ai-agent-templates/codex/AGENTS.md        ~/.codex/AGENTS.md
cp ~/ai-agent-templates/codex/hooks.json       ~/.codex/hooks.json
cp ~/ai-agent-templates/codex/hooks/session_notes.py ~/.codex/hooks/
cp ~/ai-agent-templates/codex/profiles/*.config.toml ~/.codex/
```

Then, in Codex: `/hooks` once to review and trust the three session-notes hooks (Codex skips untrusted hooks and warns at startup). The skills (`azure-cli`, `session-notes`, `kb-capture`) are referenced from the clone by `[[skills.config]]` in `config.toml` — adjust the paths if the clone lives elsewhere. Optional: the knowledge base starter in [`../knowledge-base/`](../knowledge-base/README.md).

For project-specific instructions, add an `AGENTS.md` (or `.claude/CLAUDE.md`) at the repo root; Codex concatenates the chain from the Git root to the working directory.

Windows (PowerShell): the same copies with `$HOME\.codex\…`. `hooks.json` carries `commandWindows` entries of the form `py -c "import os,runpy; runpy.run_path(os.path.expanduser('~/.codex/hooks/session_notes.py'), run_name='__main__')" stop` — Python resolves `~` itself, so the command works whichever shell Codex uses to start it (a `%USERPROFILE%` form fails under PowerShell). If `py` is a Store/PyManager alias on the machine, replace it with the full path of a real `python.exe`.

**If a hook fails:** run it by hand to see the real error — `'{"session_id":"t","hook_event_name":"SessionStart"}' | py "$HOME\.codex\hooks\session_notes.py" session-start` should print a JSON line; check `/hooks` in the TUI (trust state and the last failure per hook); and look at Codex's log under `~/.codex/log/`. A hook that errors is reported and skipped — it never stops the session — but a skipped `Stop` hook means the notes file is no longer enforced.

**Windows: `Failed to create unified exec process: CreateProcessAsUserW failed: N`.** Codex's native Windows sandbox runs every shell command as a restricted local user (`CodexSandboxOnline`/`CodexSandboxOffline`); when that user cannot start the process the command never runs and the model falls back to its own `read_file`/`apply_patch` tools (which is why reads "fail" yet still get done). **The usual cause (openai/codex #35871, 16 confirmations): the Microsoft Store / MSIX build of PowerShell 7.** Codex resolves `pwsh` through the per-user App Execution Alias (`%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe`) and Windows refuses to launch a packaged binary under the sandbox's restricted token, so every PowerShell-form command fails with error `5` (printed as `-1073283067` = `0xC0070005` on the `unelevated` backend) while `cmd.exe /c …` works — the model then routes everything through `cmd.exe`. Fix, no admin needed: turn off the `pwsh.exe` app execution alias (Settings → Apps → Advanced app settings → App execution aliases) or drop `WindowsApps` from the PATH Codex starts with, so Codex falls back to Windows PowerShell 5.1 in `System32` (launchable; verified in the thread and end to end on a corporate laptop with the Store build 7.6.6 — the model also stops routing everything through `cmd.exe`). Alternatives: install PowerShell 7 from the MSI (`C:\Program Files\PowerShell\7\pwsh.exe`) ahead of the Store one, or `windows.sandbox = "elevated"` after `codex sandbox setup --elevated`, where Codex's own fallback to an unpackaged PowerShell is active (`unelevated` also costs ConstrainedLanguage mode and the read-only tier). Other codes: `2` = program not found/executable by the sandbox user, `1312` = no logon session. Verify with `codex doctor` and `codex sandbox windows -- powershell -NoProfile -Command "Get-Date"`. Last resort: `sandbox_mode = "danger-full-access"` with `approval_policy = "on-request"` kept.

## config.toml Reference

### Model & Reasoning

**`model = "gpt-6.1-sol"`**
OpenAI's 2026 naming is *family* + *tier*: GPT-5.6 (Jul 2026), GPT-6 (Sep 2026), GPT-6.1 (Sep 2026) in tiers **Sol** (most capable), **Terra** (balanced) and **Luna** (efficient, high-volume — OpenAI describes it as roughly the nano tier; in Codex it replaced `gpt-5.4-mini`). `gpt-6.1-sol` is Codex's own default since 0.159; GPT-5.5 is retired from Codex on Oct 14 2026. On Azure, `model` is your **deployment name** — a Sol-tier deployment for agentic work, Terra (`gpt-5.6-terra`, $2/1M input) as a capable middle when Sol is not offered, Luna only as the cheap small model. A Luna-only environment should use the `luna` profile (below): the model is small, and no config setting makes a small model investigate like a large one; the AGENTS.md evidence rules do most of the work there.

**`model_reasoning_effort = "medium"`**
A free-form level whose allowed values depend on the model: the 5.6/6.x Sol and Luna tiers accept `none` (Luna) / `low` / `medium` / `high` / `xhigh` / `max`; `ultra` is GPT-6 Astra only. `medium` is the documented default for the capable tiers. Raising it does not fix shallow tool-result interpretation (an empty query taken for "no access") — that is a prompting problem, fixed in AGENTS.md. Live-tune with `Alt+,` / `Alt+.`.
- `high` as the floor for a Luna-tier model (the `luna` profile)
- `xhigh` for the `deep` profile (design, audits, debugging)

**`model_reasoning_summary = "auto"`**, **`model_verbosity = "low"`**, **`plan_mode_reasoning_effort = "high"`** — unchanged; 5.6+ is concise by default, so `low` verbosity rarely needs raising.

**`review_model`** now defaults to the session model; set a cheaper deployment only if `/review` cost matters.

**`personality`** — the schema marks the `friendly`/`pragmatic` styles deprecated; the config no longer sets it (tone lives in AGENTS.md → Output).

### Context

**`model_auto_compact_token_limit = 270000`** (the 5.6/6.x models keep GPT-5.5's 272K pricing cliff: 2× input / 1.5× output for the whole request above it)
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

**`approval_policy = "on-request"`**
`untrusted` — the value this file recommended until Oct 2026 — is **no longer supported** (Codex 0.160 rejects it), and `on-failure` is deprecated. Current values: `on-request` (interactive), `never` (non-interactive, failures go back to the model), or `{ granular = { sandbox_approval, rules, mcp_elicitations, request_permissions, skill_approval } }` to allow or auto-reject specific prompt categories. `approvals_reviewer = "auto_review"` hands eligible prompts to a reviewer subagent instead of the user.

**`sandbox_mode = "workspace-write"`** — `read-only` | `workspace-write` | `danger-full-access`, unchanged. Session overrides: `codex --full-auto`, `codex --yolo`.

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

**`hooks = true`** — lifecycle hooks from `~/.codex/hooks.json` (or inline `[hooks]`; one representation per layer). This repository ships three: `SessionStart` hands the session-notes file to the model, `Stop` continues the turn once while the notes are stale or missing, `PreCompact` records the compaction so the next stop writes the durable parts. Review and trust them once with `/hooks`; Codex re-asks when a hook definition changes. (`features.codex_hooks` is the deprecated alias.)

**`undo = true`** — git snapshot before each change, `codex undo` to roll back.
**`multi_agent = true`** — sub-agents inherit model, effort, sandbox, MCP servers and skills from the parent. *There is no `child_agents_md` setting* (older copies of this file claimed one); whether sub-agents receive the AGENTS.md chain is not documented — put the rules that must reach them into a skill the parent passes on.
**`memories = true`** — enables `[memories]`; it is the tool's summary for itself, while the session-notes file is the record the user reads.
**`prevent_idle_sleep = true`** (experimental), **`request_permissions = true`**, **`codex_git_commit = true`** — unchanged.
Removed: `js_repl` (a retired switch, rejected under Work Cloud), `features.web_search*` (use the top-level `web_search`), `personality`.

### Skills

A skill is a folder with a `SKILL.md` (name + description + the procedure). Codex selects one when the task matches its description, or you invoke it with `$name`. `[[skills.config]]` entries in `config.toml` register folders from anywhere on disk, so the shared [`../skills/`](../skills/) folder is used in place. `skills.max_context_tokens` caps the catalog shown to the model (default 2 % of the context window). Newer models follow skills closely and pause on contradictory ones — keep skills consistent with AGENTS.md.

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

**Profiles are separate files since Codex 0.134.** `codex --profile deep` loads `~/.codex/config.toml`, then overlays `~/.codex/deep.config.toml`; the overlay holds only the keys that differ. A `[profiles.name]` table in `config.toml` and the `profile = "name"` selector are ignored by current versions.

| File | Use | What it changes |
|---|---|---|
| `profiles/deep.config.toml` | hard design, audit, debugging | `model_reasoning_effort = "xhigh"`, detailed summaries |
| `profiles/fast.config.toml` | triage, extraction, transforms | a Luna-tier model at `low`, no approval prompts |
| `profiles/luna.config.toml` | an environment that only has a Luna-tier deployment | `model = "gpt-5.6-luna"`, `high` effort, concise summaries |

The GPT-5.1 federal profile under `profiles/gpt-5.1/` is a full config for that environment (not an overlay).

## TUI Reasoning Hotkeys (Codex v0.124.0+)

- `Alt+,` — lower reasoning effort one step
- `Alt+.` — raise reasoning effort one step
- Switching models resets reasoning to the new model's default rather than preserving your last setting

---

## AGENTS.md Reference

The coaching file loaded at session start. Codex auto-discovers `AGENTS.md` files from repo root down to the working directory, with later directories overriding earlier ones; the model has been trained to closely adhere to these injected instructions.

### Why this AGENTS.md is short — and what the Oct 2026 additions are for

OpenAI's guidance for GPT-5.6 and GPT-6: leaner prompts score higher and spend fewer tokens; state autonomy boundaries once; do not ask the model to "think harder"; the newest models are *more* sensitive to instructions in AGENTS.md and skills and will pause early on contradictory ones. So this file stays short and is audited for conflicts.

Four sections were added in Oct 2026 after a real incident (a Luna-tier model ran an Azure CLI command with a malformed `--query`, got `[]`, and reported "your account has no access"):

- **Initiative** — OpenAI's own persistence pattern in plain words: bias toward action, persist to the intended goal, come back with a reviewable result, boundaries stated once.
- **Evidence Rules (tool results)** — the rule the incident lacked: an empty result has four likelier causes than permission; bisect a filtered command back to its simplest form; read exit code and stderr; every environment claim quotes the command and the output line; three *different* attempts before a hand-back; verified vs inferred kept apart.
- **Session Notes / Knowledge Base / Skills** — the practices from a multi-machine Claude Code setup, made tool-agnostic: a notes file a new session boots from (enforced by the hooks), a small knowledge base the agent reads first and gives back to, and reusable procedures as skills.

For GPT-5.1, `profiles/gpt-5.1/AGENTS.md` keeps the heavier reasoning coaching that model needs, plus the same four sections.

### Key sections and why they're worded the way they are

**Role / Goal / Success Criteria** — Defines the destination, not the path. Lets the model choose the most efficient route. Per OpenAI: "describe what good looks like, what constraints matter, what evidence is available, and what the final answer should contain."

**Constraints** — Tool preferences and code-quality rules that genuinely apply across tasks. Things like "prefer `apply_patch` over shell" matter because the model was trained specifically on `apply_patch`.

**Output** — Explicit `verbosity: low`, no upfront-plan/preamble requirement, hard floor on update cadence. The "no preamble" guidance is critical: Codex prompting guide explicitly warns that prompting for status updates "can cause the model to stop abruptly before the rollout is complete."

**Stop Rules** — How to know when to bail out. "Don't end the turn with only a plan" comes directly from the official Codex prompt: "Unless asked for a plan, never end the interaction with only a plan."

**Git Safety** — Uses a developer-instinct framing rather than explicit prohibitions. From a real incident where GPT force-pushed `.gitignore`d files: telling a model "never commit .claude/" leads to it obsessively caveating "and not the .claude folder" on every response. Framing it as "treat .claude/ like .vs/ — would you think twice about committing .vs?" gets the model to internalize the principle. Concrete guardrails (no force-push, always check `git status`) still included but lead with the intuition.

**Session Continuity** — Codex's server-side encrypted compaction (OpenAI provider) preserves instructions reliably. No instruction-loss issue like OpenCode pre-fix. The session context file is still useful for resuming across sessions.

---

## Recent Codex CLI Updates (Oct 2026)

| Version / date | Highlights |
|---|---|
| 0.160.1 (Oct 5 2026) | current stable |
| 0.159.1 (Sep 29) | **GPT-6.1 Sol** is the default model |
| 0.156.1 (Sep 22) | GPT-6 Sol and GPT-6 Luna available |
| Jul 31 | `gpt-5.6-luna` replaces `gpt-5.4-mini` as the small model; GPT-5.5 scheduled to retire from Codex Oct 14 2026 |
| 0.134.0 | `[profiles.*]` tables retired — profiles are `~/.codex/<name>.config.toml` overlays |
| 0.124.0 (Apr 23) | `Alt+,` / `Alt+.` reasoning hotkeys; hooks stable in `config.toml` |

Source: https://developers.openai.com/codex/changelog and the config reference, checked 2026-10-05.

## Per-project Setup

Add a `.codex/config.toml` at the repo root to override settings for that project:

```toml
# .codex/config.toml
model = "gpt-6.1-sol"            # or the Azure deployment name of a Sol-tier model
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
