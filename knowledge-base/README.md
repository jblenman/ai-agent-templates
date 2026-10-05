# Knowledge base starter

A small, tool-agnostic knowledge base that Codex CLI, OpenCode and Claude Code sessions read at start and add to as they work. It is the generic form of a practice that pays for itself in a week: the next session starts from what the last one learned instead of rediscovering it.

## Layout

```
KB.md              the instruction block the agent loads (read-first rules, give-back rules, the "KB:" line)
kb/index.md        read first; one row per file with "read when"
kb/overview.md     what the systems are, terms, owners
kb/dev/codebase.md build/run/test/debug as they really work
kb/dev/gotchas.md  symptom → cause → fix
kb/env/environments.md  environments, accounts, what may be touched (no secrets)
kb/decisions.md    decisions with reasons and rejected alternatives, newest first
kb/tools/<tool>.md how a tool really behaves (copy _TEMPLATE.md)
kb/known-issues.md defects and intended oddities
```

## Set up — one person

1. Copy this folder somewhere outside any project, e.g. `~/knowledge-base/` (or inside the project as `docs/kb/` if the knowledge is project-only).
2. Import `KB.md` from your global instructions, with the folder's path on the same line so the agent can resolve `<kb>`:
   - Codex CLI, `~/.codex/AGENTS.md`: a line `Knowledge base: ~/knowledge-base — read its KB.md at session start.` plus the contents of `KB.md` pasted below it (Codex reads AGENTS.md as plain text; it does not follow `@` imports).
   - Claude Code, `~/.claude/CLAUDE.md`: `@~/knowledge-base/KB.md` (one approval the first time).
   - OpenCode, `~/.config/opencode/AGENTS.md`: paste as for Codex.
3. Install the `kb-capture` skill (see [`../skills/`](../skills/)) so capture follows the house format.

## Set up — a team

Make the folder a git repository (`git init`, push it to your host), have everyone clone it to the same path, and keep the import lines above. Sessions then write on `kb/<topic>` branches and open pull requests (the `kb-capture` skill does this when it sees `<kb>/.git`); someone merges weekly. Protect `main`.

## Rules worth keeping even if you change everything else

- Read-first: the index before any exploration, every time.
- Give-back in the same session: what cost time, what was wrong, what was decided.
- Topic-based files, one fact per line, exact commands and error text, a `last_verified` date.
- Never secrets, never production or personal data, never anything your organization classifies as non-public when the knowledge base lives outside that boundary, never one session's running state (that is the session-notes file).
- Every reply ends with a `KB:` line, so the person can see what was recorded without opening the folder.
