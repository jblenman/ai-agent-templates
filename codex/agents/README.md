# Codex custom agents

Standalone TOML files, one agent each — personal agents in `~/.codex/agents/`, project agents in `<repo>/.codex/agents/`. Codex loads the file as a config layer for the spawned session: `name`, `description` and `developer_instructions` are required; `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers` and `skills.config` are optional and inherit from the parent when omitted. Built-ins are `default`, `worker` and `explorer`; a custom agent with the same name wins (the `explorer` here does that, adding the evidence rules).

Install: `cp ~/ai-agent-templates/codex/agents/*.toml ~/.codex/agents/`, then set `model` in `explorer.toml` and `scribe.toml` to your cheap deployment (they default to `gpt-6-luna`). `[agents]` defaults live in `config.toml`.

Use: ask for them — "spawn the reviewer and the security auditor on this branch, wait for both, summarize by severity" — or let an AGENTS.md or skill instruction request delegation. `/agent` switches between running threads; approvals from a background thread show the source thread and `o` opens it. The parent's live overrides (`/permissions`, `--yolo`) override an agent file's `sandbox_mode`. Whether a subagent receives the AGENTS.md chain is not documented, so each file carries the rules it needs. Every agent spends its own tokens; use them for read-heavy, parallel work (exploration, review, tests, triage), not for parallel editing.

| Agent | Model | Sandbox | Job |
|---|---|---|---|
| `explorer` | Luna tier, high | read-only | evidence gathering with the evidence rules |
| `reviewer` | parent | read-only | correctness, security, regressions, missing tests |
| `qa_tester` | parent | parent | run existing tests, add missing cases, report verbatim |
| `security_auditor` | parent, high | read-only | OWASP classes, secrets, SSRF, paths, dependencies |
| `scribe` | Luna tier | parent | docs, session notes, knowledge-base captures |

Source: https://developers.openai.com/codex/agent-configuration/subagents (checked 2026-10-06).
