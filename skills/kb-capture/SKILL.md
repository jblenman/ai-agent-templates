---
name: kb-capture
description: Save what this session learned into the knowledge base — a gotcha, a setup or build step, an environment fact, a tool quirk, a decision with its reason, a known issue — in the right file, in the house format, with the index updated; and for a shared knowledge base, on a branch with a pull request. Use at the end of any task that cost real time to figure out, or when the user says "remember this" / "add that to the KB".
argument-hint: "[what to capture]"
---

# Capture knowledge

Capture: $ARGUMENTS

If that is empty, go through this session and list what a later session would have wanted to know at the start. When the list is not obvious, confirm it with the user first.

`<kb>` below is the knowledge base folder named in your instructions (the line next to the import of `KB.md`). Look for `<kb>/.git`: if it exists the knowledge base is a shared git repository (do every section); if not, it is one person's folder or lives inside the project repository (skip sections 1 and 5).

## 1. Prepare (shared repository only)

1. `git -C "<kb>" status --short --branch`. Changes you did not make, or a clone not on `main` → stop and tell the user.
2. `git -C "<kb>" branch --list "kb/*"` — branches from earlier sessions not merged yet. Tell the user which exist; if one covers what you are about to write, continue on it instead of opening a second.
3. Otherwise `git -C "<kb>" pull --ff-only`, then `git -C "<kb>" switch -c kb/<topic>`.

## 2. Put it where it belongs

| What you learned | Where |
|---|---|
| Something that cost time: a build, environment, CLI, dependency or data quirk | `kb/dev/gotchas.md` (one entry per quirk: symptom, cause, fix) |
| How to build, run, test or debug this codebase | `kb/dev/codebase.md` |
| An address, account, role, subscription, region or environment rule | `kb/env/environments.md` |
| A decision and its reasons (and the alternatives rejected) | `kb/decisions.md` — one dated entry, newest first |
| How a tool or service actually behaves (not what its docs promise) | `kb/tools/<tool>.md` |
| A defect or oddity that is intended | `kb/known-issues.md` |
| A term, a system, a role: what it is | `kb/overview.md` |

Extend an existing file first; create a file only for a new topic, and add it to `kb/index.md` with a one-line "read when" hint.

## 3. Format rules

- Topic-based, not chronological: add to the matching section; do not append dated journal entries (decisions are the one dated file).
- One fact per bullet; tables for comparisons; the exact command, error text, path or version — vague summaries lose their value.
- State what was verified and when (`last_verified: 2026-10-05` in a file's front matter, or "(checked 2026-10-05)" on the line). Do not write what you have not verified; mark a guess as a guess or leave it out.
- Correct what you find wrong while you are there. Remove what is dead.
- Write for a reader who was not in this session: no "as discussed", no session ids, no narrative.

## 4. Never write

Passwords, tokens, keys, connection strings; real personal or production data; anything your organization classifies as non-public (internal system names, data, documents) when the knowledge base is not inside that boundary; screenshots or other evidence files; notes about one session's state (that is the session-notes file); anything unverified.

## 5. Review and share (shared repository only)

Re-read the diff as the next reader: does each entry say where, when, and how it was verified? Then `git -C "<kb>" add -A && git -C "<kb>" commit -m "kb: <topic>"`, push the branch, and open a pull request (or tell the user the branch name if you cannot). Never commit to `main` directly in a shared knowledge base.

## 6. Say what you did

End the reply with one line: `KB: kb/dev/gotchas.md +1 (az --query returns [] for an unknown field)` or `KB: nothing new`. For a shared repository add the branch and whether it was pushed.
