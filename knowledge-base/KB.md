# Knowledge base

This folder holds **general, reusable technical knowledge** that agent sessions share: how tools really behave, patterns that worked, language gotchas, standards and conventions — things that would still be true and useful in a different project next year. It is not the record of current work.

## The test — what belongs here and what does not

Ask one question before writing: **would this still be true, and useful to someone else, in another project six months from now?**

| Belongs here (knowledge) | Does not belong here (state and project context) |
|---|---|
| How a tool or service actually behaves, with the command and the date verified: "`az … --query` returns `[]` on an unknown field; strings must be single-quoted" | What the current task is, what was done today, what is in progress, what is blocked — that is the **session-notes file** |
| A pattern that solved a class of problem, with when to use it and when not | Decisions about *this* project and their reasons (which option we chose, who owns what) — those go to the project's `AGENTS.md`, its notes file or its design docs |
| A language or framework gotcha, with the symptom, the cause and the fix | Descriptions of this project's systems, environments, accounts, data model, team — project context, not knowledge |
| A standard or convention and the reason behind it | Anything that only makes sense if you know what we were working on |
| A measurement that changes a default ("compaction at 270K avoids the 272K surcharge") | Logs, outputs, evidence files, screenshots |

Wording test: if an entry needs "we", "currently", "today", "this repo" or "the migration" to make sense, it is state. Rewrite it as a general fact or leave it out.

## Read before you explore

- Before any task, scan `kb/index.md` and read the files whose "read when" matches the task — before searching, before running discovery commands, before asking the user something the knowledge base already answers.
- Trust what is here and do not re-verify it for its own sake. Exceptions: an entry marked `last_verified: never`, or anything that contradicts what you observe — then verify and correct the entry.

## Give back what you learn

Keeping this knowledge base current is part of every task, not extra work. In the same session, when any of these happens, write it down — **as general knowledge, stripped of the project**:

| When | Write |
|---|---|
| A tool or service behaved differently from its docs, and you proved how | `kb/tools/<tool>.md` |
| Something cost real time to figure out and will cost the next person the same | the matching tool, pattern or language file: symptom → cause → fix |
| A pattern or approach worked (or failed) in a way that transfers to other projects | `kb/patterns/<topic>.md` |
| A language, framework or runtime gotcha | `kb/languages/<language>.md` |
| A documented default, standard or convention was wrong | the fix, with today's date as `last_verified` |

Use the `kb-capture` skill: it applies the test above, holds the format rules, and does the branch-and-pull-request steps for a shared knowledge base. Do not ask whether to record something that passes the test; writing it down is yours to do. **Never** update a knowledge-base file to reflect the state of current work — that is what the session-notes file is for.

Never write here: passwords, tokens, keys, connection strings; real personal or production data; anything your organization classifies as non-public when this knowledge base lives outside that boundary; unverified claims; one session's or one project's state.

## Say what you did

End every reply that follows work with one line: `KB: kb/tools/azure-cli.md +1 (JMESPath strings are single-quoted)` or `KB: nothing new`. For a shared repository add the branch and whether it was pushed.

## Index

@kb/index.md
