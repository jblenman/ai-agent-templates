// ~/.config/opencode/plugins/session-notes.js  (or <repo>/.opencode/plugins/)
//
// Keeps the session-notes file alive in OpenCode the way a Stop hook does in Claude Code and Codex:
//   - when a session goes idle while the notes file is stale or missing, send the session one
//     follow-up prompt asking for the update (at most once per cooldown, so it can never loop);
//   - at compaction, add the notes rule to the compaction context so the summary keeps it;
//   - at session start, inject the notes file as context (no reply) so the model boots from it.
//
// Plugin API: https://opencode.ai/docs/plugins (hooks `event`, `experimental.session.compacting`,
// `client.session.prompt` with `noReply`), checked against the plugin types on 2026-10-05.
// Written for OpenCode 1.18.x. Not exercised live by the author — report issues at the repo.
//
// Environment:
//   SESSION_NOTES             notes file (default ~/.config/opencode/session-notes.md)
//   SESSION_NOTES_STALE_MIN   minutes before the file counts as stale (default 30)
//   SESSION_NOTES_COOLDOWN_MIN minutes between nudges for one session (default 30)
//   SESSION_NOTES_HEAD_LINES  lines of the file injected at session start (default 80)
//   SESSION_NOTES_GUARD=off   disable the nudge (the start-of-session context still loads)

import { stat, readFile } from "node:fs/promises"
import { homedir } from "node:os"
import { join } from "node:path"

const env = (k, d) => (process.env[k] && process.env[k].trim()) || d
const notesPath = () => env("SESSION_NOTES", join(homedir(), ".config", "opencode", "session-notes.md"))
const off = () => ["off", "0", "false", "no"].includes(env("SESSION_NOTES_GUARD", "").toLowerCase())

async function ageMinutes(path) {
  try {
    const s = await stat(path)
    return (Date.now() - s.mtimeMs) / 60000
  } catch {
    return null
  }
}

function sessionIdOf(event) {
  const p = event?.properties ?? {}
  return p.sessionID ?? p.info?.id ?? p.session?.id ?? null
}

export const SessionNotesPlugin = async ({ client }) => {
  const staleMin = Number(env("SESSION_NOTES_STALE_MIN", "30"))
  const cooldownMs = Number(env("SESSION_NOTES_COOLDOWN_MIN", "30")) * 60000
  const headLines = Number(env("SESSION_NOTES_HEAD_LINES", "80"))
  const nudged = new Map() // sessionID -> last nudge time
  const booted = new Set() // sessions that already received the notes as context

  const nudge = async (sessionID, text) => {
    const last = nudged.get(sessionID) ?? 0
    if (Date.now() - last < cooldownMs) return
    nudged.set(sessionID, Date.now())
    await client.session.prompt({ path: { id: sessionID }, body: { parts: [{ type: "text", text }] } })
  }

  return {
    event: async ({ event }) => {
      const sessionID = sessionIdOf(event)
      if (!sessionID) return
      const path = notesPath()

      if (event.type === "session.created" && !booted.has(sessionID)) {
        booted.add(sessionID)
        let context
        try {
          const lines = (await readFile(path, "utf8")).split("\n")
          const more = lines.length > headLines ? ` (${lines.length - headLines} more lines in the file)` : ""
          context = `Session notes from ${path}${more} — read before starting, and keep this file current during the session:\n\n${lines.slice(0, headLines).join("\n")}`
        } catch {
          context = `No session-notes file exists yet at ${path}. Create it in your first tool-using turn (session-notes skill): tasks and status, decisions with reasons, files touched, open threads, with an "Updated: <real clock>" line at the top.`
        }
        try {
          await client.session.prompt({ path: { id: sessionID }, body: { noReply: true, parts: [{ type: "text", text: context }] } })
        } catch {}
        return
      }

      if (event.type === "session.idle" && !off()) {
        const age = await ageMinutes(path)
        if (age === null) {
          await nudge(sessionID, `Before finishing: the session-notes file ${path} does not exist. Create it now (session-notes skill: tasks and status, decisions with their reasons, files touched, open threads; "Updated: <real clock>" at the top), then give the one-line answer you were about to give.`)
        } else if (age > staleMin) {
          await nudge(sessionID, `Before finishing: ${path} was last updated ${Math.round(age)} minutes ago. Update it now — what was done, decisions with their reasons, files touched, what is open — and its "Updated:" line, then finish with one line saying the notes were updated.`)
        }
      }
    },

    "experimental.session.compacting": async (_input, output) => {
      output.context.push(
        `Carry forward the session-notes rule: ${notesPath()} is the record a new session boots from — after this compaction, write the durable parts of what came before (decisions with reasons, identifiers, files touched, open threads) into it before doing anything else.`,
      )
    },
  }
}
