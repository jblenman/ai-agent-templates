# Claude Code — Global Instructions
# https://github.com/jblenman/ai-agent-templates
#
# Global instruction file — place at ~/.claude/CLAUDE.md
# Add a project-level .claude/CLAUDE.md at the repo root for project-specific context.
# Keep this file concise — content loads into the context window every session.

## Workflow

For any non-trivial task, explore before acting:
1. Read relevant files and understand the current state
2. State your plan before making changes — use plan mode (`shift+tab`) for complex tasks
3. Implement
4. Verify

If something turns out to be larger in scope than it appeared, surface it before continuing.

When stuck, explain what you tried and why it isn't working. Don't retry the same failing approach. Consider alternative angles or ask.

## Communication

- Be direct and concise. No filler phrases.
- Lead with the answer or action, then explain if needed.
- State assumptions explicitly rather than asking for clarification on minor ambiguities.
- Ask when a decision has significant consequences or the right path is genuinely unclear.

## Code Quality

- Write the simplest code that solves the problem. Don't over-engineer.
- Don't add features, refactors, or "improvements" that weren't asked for.
- Don't add comments or docstrings to code you didn't change.
- Don't add error handling for things that can't happen. Only validate at system boundaries.
- Prefer editing existing files over creating new ones.
- Don't create documentation files unless explicitly asked.
- Don't add backwards-compatibility shims for things that are simply being changed.

## Git

- Never commit unless explicitly asked.
- When committing, stage specific files — not `git add -A` or `git add .` without first checking `git status`.
- Never force-push to main/master.
- Never skip hooks (`--no-verify`) unless explicitly asked.
- Don't amend published commits.
- When in doubt about whether to include a file, ask.

## Session Context

Maintain `~/.claude/session-context.md` to track:
- Current task and status
- Key decisions made
- Files modified
- What's done, in progress, and remaining
- Any background tasks (IDs, what they're doing)

Update it after significant steps. A new session should be able to read it and resume with minimal ramp-up.
