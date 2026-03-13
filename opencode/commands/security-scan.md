---
description: Run a security audit on current code or specified files
agent: security-auditor
---
Perform a security audit on the specified scope.

If no specific target is given, audit all files changed in the current branch vs main (`git diff main...HEAD --name-only`) plus any uncommitted changes.

$ARGUMENTS
