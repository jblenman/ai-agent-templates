# Index — read this first, then only what the task needs

Topic-based, not chronological. One file per tool, pattern or language; a new file gets a row here with "read when" in the words a person would use.

| File | Read when | Holds |
|---|---|---|
| [tools/_TEMPLATE.md](tools/_TEMPLATE.md) | you are about to create a tool file | the shape of a tool entry |
| [patterns/_TEMPLATE.md](patterns/_TEMPLATE.md) | you are about to create a pattern file | the shape of a pattern entry |
| [languages/_TEMPLATE.md](languages/_TEMPLATE.md) | you are about to create a language file | the shape of a language entry |

Examples of rows this index grows into:

| File | Read when | Holds |
|---|---|---|
| tools/azure-cli.md | any task that runs `az` | login/scope checks, JMESPath quoting, what empty results and error texts mean, extensions vs core |
| patterns/retry-and-backoff.md | calling a flaky remote service | idempotency, jitter, when a retry hides a real failure |
| languages/python.md | writing Python that must run on 3.8 and Windows | syntax floor, CP1252 console encoding, subprocess encoding |

What is **not** indexed here: the current task, this project's systems, environments, decisions and status — those live in the session-notes file and the project's own `AGENTS.md`/docs.
