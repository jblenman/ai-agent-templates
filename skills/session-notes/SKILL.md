---
name: session-notes
description: Keep the session-notes file that a new session boots from — what to record (tasks and status, decisions with their reasons, files touched, background work, open threads), when to update it (after each significant step, after any decision, before a long operation, right after compaction), the file layout, and when a project gets its own file. Use at session start, after decisions, and before ending a tool-using turn.
---

# session-notes: the record a new session boots from

An agent session loses its memory when it ends, when its context is compacted, or when the terminal is closed. The session-notes file is the record that survives: short enough to read in a minute, complete enough to resume from. Keeping it current is part of every task, not extra work after it.

**The file:** `~/.claude/session-notes.md` (Claude Code) and `~/.config/opencode/session-notes.md` (OpenCode) — one per machine, shared by every session on it. **Codex CLI uses `<workspace>/session-notes.md` by default**, because its `workspace-write` sandbox blocks writes outside the workspace and protects `.codex`/`.git` folders even inside it (a file under `~/.codex` cannot be written from the sandbox at all). When one person uses several tools, set `SESSION_NOTES=<one path>` in the environment and every tool keeps the same file; for Codex also add that file's folder to `sandbox_workspace_write.writable_roots` in `config.toml` — never `~/.codex` itself, which would let the model edit its own config and hooks. Project-scoped work may use `SESSION-NOTES.md` at the repo root instead (git-ignored or committed, the team's choice).

## What to record

- **What is being worked on** and its status: done, in progress, remaining.
- **Decisions and their reasons**, including alternatives rejected and why. An outcome without its reasoning gets re-litigated by the next session.
- **Files created or changed** (paths), identifiers that matter (commands, branch names, ids, error texts verbatim).
- **Background work still running**: what it does, where its log is, how to check it.
- **Open threads, blockers, questions for the user.** Half-finished thinking matters more than finished work: finished work is in the files, open threads exist only in the conversation.
- **Corrections and preferences the user stated** ("don't do X", "yes, that is right"): durable, and cheap to carry.

Keep it brief and scannable: headings, bullets, one line per fact. A dated line at the top (`Updated: 2026-10-05 00:40`) tells the reader how fresh it is. Write the real clock, never an estimate.

## When to update

- At the start of a session: read the file, note the previous state, add or refresh a section for this session.
- After completing a significant step; before and after a long-running operation; when switching tasks.
- **After any decision reached in discussion**, even when no file changed. A question-and-answer turn that settles what will be done is the most often lost record.
- Before ending a turn that used tools while the file is more than ~30 minutes stale.
- Right after a compaction: the compaction summary may now be the only record of what came before it. Write the durable parts into the file first.

End a reply that follows tool use or a decision with one line saying what was recorded (for example `Notes: session-notes updated (decision on the parser rewrite, files touched).`), so the user sees it without opening the file. Where a hook enforces freshness (Claude Code's session-guard plugin), updating *before* it has to saves the extra turn; without a hook, this rule is the only enforcement — follow it anyway.

## Layout of the file

```markdown
# Session notes -- <machine name>
Updated: 2026-10-05 00:40

## <Task or project A>
- Status: ...
- Decisions: ... (why ...)
- Files: ...
- Open: ...

## <Task or project B>
...

## Background
- <task>: <what it does>, log <path>, check with <command>
```

Ad-hoc work (a question answered, a small fix, a one-off task) records its state inline here. Do not create a project file for it, and do not create a catch-all "general" project: that is what this file is.

## When a project outgrows the shared file

Split a project into a notes file of its own **only when both hold**: another session on this machine is updating the shared file in the same timeframe, **and** the work is an ongoing multi-session project with real state (a mission, decisions, open threads), not an afternoon's task. Then the shared file keeps a one-line index row pointing at the project file, bumped in the same turn as the project file.

## Relation to the knowledge base

The notes file is **state**: this work, now. The knowledge base is **knowledge**: what would still be true in another project next year. A decision about this project, the status of a migration, what the systems here are — notes (or the project's instructions). How a tool behaved, a pattern that transferred, a language gotcha — knowledge base, stripped of the project, through the `kb-capture` skill. When in doubt, it is notes; promoting a general fact to the knowledge base later is cheap, and a knowledge base full of project state is useless to the next project.

## Relation to the tool's own memory

Codex's `[memories]` and Claude Code's auto-memory are summaries the tool makes for itself; this file is the explicit record the user reads and the next session resumes from. Keep both; they answer different questions.
