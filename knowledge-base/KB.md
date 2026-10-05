# Knowledge base

This folder is the memory that agent sessions on this project (or this machine) share: what the systems are, how to build, run and test them, what has cost time before, which environments exist and what may be touched in them, and the decisions already made with their reasons. A session loads this file at start; the paths below are relative to this folder.

## Read before you explore

- Before any task, scan `kb/index.md` and read every file whose "read when" matches the task — before searching the codebase, before running discovery commands, before asking the user something the knowledge base already answers.
- Trust what is here and do not re-verify it for its own sake. Exceptions: a file or entry marked `last_verified: never`, or anything that contradicts what you observe — then verify, and correct the entry.
- If what you need is not in the index, list the `kb/` folder once before concluding it is not written down.

## Give back what you learn

Keeping this knowledge base current is part of every task, not extra work. In the same session, when any of these happens, write it down:

| When | Write |
|---|---|
| Something cost real time to figure out (setup, build, a CLI quirk, data, an environment rule) | An entry in `kb/dev/gotchas.md` or the matching file |
| A documented command, path, address or step was wrong | The fix, with today's date as `last_verified` |
| A decision was made (by you or the user) that a later session must not re-open | A dated entry in `kb/decisions.md` with the reasons and the alternatives rejected |
| You learned how a tool or service really behaves | `kb/tools/<tool>.md` |
| You hit a defect or oddity not in `kb/known-issues.md` | A row there |

Use the `kb-capture` skill: it holds the file map, the format rules and the review steps for a shared knowledge base. Do not ask whether to record something; writing it down is yours to do.

Never write here: passwords, tokens, keys, connection strings; real personal or production data; anything your organization classifies as non-public when this knowledge base lives outside that boundary; screenshots; anything unverified; one session's running state (that belongs in the session-notes file).

## Say what you did

End every reply that follows work with one line: `KB: kb/dev/gotchas.md +1` or `KB: nothing new`. For a shared repository add the branch and whether it was pushed.

## Index

@kb/index.md
