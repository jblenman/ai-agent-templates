# Knowledge base starter

A small, tool-agnostic knowledge base that Codex CLI, OpenCode and Claude Code sessions read at start and add to as they work — **general, reusable technical knowledge**: how tools really behave, patterns that worked, language gotchas, standards and the reasons behind them. The next session starts from what the last one learned instead of rediscovering it.

It is deliberately **not** a place for the current work. Three records, three jobs:

| Record | Holds | Lives in |
|---|---|---|
| **Session notes** | what is being worked on, status, decisions made *in this work* with their reasons, files touched, open threads | the session-notes file (per machine or per workspace) |
| **Project context** | what this project's systems are, environments, accounts, conventions, who owns what | the project's `AGENTS.md` / `CLAUDE.md` and its docs |
| **Knowledge base** (this) | facts that would still be true and useful in another project next year | `kb/tools/`, `kb/patterns/`, `kb/languages/` |

The first version of this starter blurred the lines (it shipped an `overview.md`, a `decisions.md` and an `environments.md`), and agents duly filled them with project state. The test in `KB.md` — *would this still be true, and useful to someone else, in another project six months from now?* — is now the gate, in the instructions and in the `kb-capture` skill.

## Layout

```
KB.md                      the instruction block the agent loads: the test, read-first and give-back rules, the "KB:" line
kb/index.md                read first; one row per file with "read when"
kb/tools/<tool>.md         how a tool or service really behaves (verified, dated)
kb/patterns/<topic>.md     an approach that transfers between projects: problem, approach, when not to use it
kb/languages/<language>.md gotchas and conventions for a language, framework or runtime
kb/*/_TEMPLATE.md          the shape of each kind of entry
```

## Set up — one person

1. Copy this folder somewhere outside any project, e.g. `~/knowledge-base/`.
2. Import `KB.md` from your global instructions, with the folder's path on the same line so the agent can resolve `<kb>`:
   - Codex CLI, `~/.codex/AGENTS.md`: a line `Knowledge base: ~/knowledge-base — read its KB.md at session start.` plus the contents of `KB.md` pasted below it (Codex reads AGENTS.md as plain text).
   - Claude Code, `~/.claude/CLAUDE.md`: `@~/knowledge-base/KB.md` (one approval the first time).
   - OpenCode, `~/.config/opencode/AGENTS.md`: paste as for Codex.
3. Install the `kb-capture` skill (see [`../skills/`](../skills/)) so capture follows the test and the house format.

## Set up — a team

Make the folder a git repository (`git init`, push it to your host), have everyone clone it to the same path, and keep the import lines above. Sessions then write on `kb/<topic>` branches and open pull requests (the `kb-capture` skill does this when it sees `<kb>/.git`); someone merges weekly. Protect `main`.

## Rules worth keeping even if you change everything else

- The test: another project, next year, still true and useful → knowledge base; otherwise notes or project context.
- Read-first: the index before any exploration, every time.
- Give-back in the same session, stripped of the project: no "we", "currently", "today", "this repo".
- Topic-based files, one fact per line, exact commands and error text, a `last_verified` date; correct what you find wrong.
- Never secrets, never production or personal data, never anything your organization classifies as non-public when the knowledge base lives outside that boundary, never one session's or project's state.
- Every reply ends with a `KB:` line, so the person can see what was recorded without opening the folder.
