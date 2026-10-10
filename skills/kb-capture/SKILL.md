---
name: kb-capture
description: Save what this session learned into the knowledge base — general, reusable technical knowledge only (how a tool really behaves, a pattern that transfers, a language gotcha, a standard and its reason) in the right topic file, in the house format, with the index updated; for a shared knowledge base, on a branch with a pull request. Applies the test "still true and useful in another project next year?" and refuses project state. Use at the end of any task that cost real time, or when the user says "remember this" / "add that to the KB".
argument-hint: "[what to capture]"
---

# Capture knowledge

Capture: $ARGUMENTS

If that is empty, go through this session and list what a later session **on a different project** would want to know. Most of what a session learns is about the current work; that is for the session-notes file, not for here. Expect the list to be short.

`<kb>` below is the knowledge base folder named in your instructions (the line next to the import of `KB.md`). Look for `<kb>/.git`: if it exists the knowledge base is a shared git repository (do every section); if not, it is one person's folder (skip sections 1 and 5).

## 0. The gate — apply it to every candidate before writing

**Would this still be true, and useful to someone else, in another project six months from now?**

- Yes, as written → capture it (section 2).
- Yes, once the project is stripped out → rewrite it as a general fact first: no "we", "currently", "today", "this repo", "the migration", no system or team names. If nothing general remains, it was state.
- No → it is **state or project context**. Put it where it belongs instead: current task, status, decisions made in this work → the session-notes file; this project's systems, environments, accounts, conventions, owners → the project's `AGENTS.md`/docs. **Do not create or update a knowledge-base file to reflect current work** — no "overview" of the project, no running status, no decision log.

## 1. Prepare (shared repository only)

1. `git -C "<kb>" status --short --branch`. Changes you did not make, or a clone not on `main` → stop and tell the user.
2. `git -C "<kb>" branch --list "kb/*"` — branches from earlier sessions not merged yet. Tell the user which exist; if one covers what you are about to write, continue on it instead of opening a second.
3. Otherwise `git -C "<kb>" pull --ff-only`, then `git -C "<kb>" switch -c kb/<topic>`.

## 2. Put it where it belongs

| What you learned | Where |
|---|---|
| How a tool or service actually behaves (not what its docs promise): a command that works or fails, a quirk, a version-specific change | `kb/tools/<tool>.md` |
| An approach that solved a class of problem and transfers: when to use it, when not, what it cost or saved | `kb/patterns/<topic>.md` |
| A language, framework or runtime gotcha: symptom → cause → fix | `kb/languages/<language>.md` |
| A standard or convention and the reason behind it | the matching tool, pattern or language file |

Extend an existing file first (one file per tool, pattern or language); create a file only for a new topic, from the folder's `_TEMPLATE.md`, and add it to `kb/index.md` with a one-line "read when" hint in the words a person would use.

## 3. Format rules

- Topic-based, not chronological: add to the matching section; never append dated journal entries.
- One fact per bullet; tables for comparisons; the exact command, error text, path or version — vague summaries lose their value.
- Say what was verified and when: `last_verified: <date>` in the file's front matter, or "(checked <date>, version <x>)" on the line. Do not write what you have not verified; mark a guess as a guess or leave it out.
- Correct what you find wrong while you are there. Remove what is dead.
- Write for a reader who was not in this session and is not on this project.

## 4. Never write

Passwords, tokens, keys, connection strings; real personal or production data; anything your organization classifies as non-public (internal system names, data, documents) when the knowledge base lives outside that boundary; screenshots or other evidence files; one session's or one project's state; anything unverified.

## 5. Review and share (shared repository only)

Re-read the diff as a reader on another project: does each entry stand on its own, say how and when it was verified, and name no project? Then `git -C "<kb>" add -A && git -C "<kb>" commit -m "kb: <topic>"`, push the branch, and open a pull request (or tell the user the branch name if you cannot). Never commit to `main` directly in a shared knowledge base.

## 6. Say what you did

End the reply with one line: `KB: kb/tools/azure-cli.md +1 (JMESPath strings are single-quoted)`, `KB: nothing new`, or `KB: nothing new — the findings were project state, written to the session notes`. For a shared repository add the branch and whether it was pushed.
