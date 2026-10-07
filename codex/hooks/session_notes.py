"""Codex CLI lifecycle hooks that keep the session-notes file alive.

    python3 session_notes.py session-start   # SessionStart: hand the notes to the model as context
    python3 session_notes.py stop            # Stop: continue the turn once while the notes are stale or missing
    python3 session_notes.py pre-compact     # PreCompact: remember that a compaction happened
    python3 session_notes.py status          # what the hooks would decide right now

Contract (developers.openai.com/codex/hooks): one JSON object on stdin, JSON on stdout.
A Stop hook that prints {"decision": "block", "reason": ...} makes Codex continue the turn with the
reason as a new prompt; `stop_hook_active` is true when that already happened this turn, so the
hook never loops. Exit 0 with no output means "nothing to say". Every failure path exits 0:
a broken hook must never stop a session.

Configuration (environment):
  SESSION_NOTES              path of the notes file (default: <workspace>/.codex/session-notes.md, from the event's cwd)
  SESSION_NOTES_STALE_MIN    minutes before the file counts as stale at a Stop (default 30)
  SESSION_NOTES_HEAD_LINES   how many lines SessionStart hands to the model (default 80)
  SESSION_NOTES_GUARD=off    disable the Stop check (headless runs, throwaway sessions)

Stdlib only, Python 3.8+. Windows: the hooks.json entry uses `commandWindows` with the `py` launcher.
"""
import json
import os
import sys
import time
from pathlib import Path


def notes_path(cwd=None):
    """SESSION_NOTES if set; else <workspace>/.codex/session-notes.md — inside the workspace, because the
    workspace-write sandbox blocks writes anywhere else (a file under ~/.codex would need an escalation
    on every update). For a machine-wide file set SESSION_NOTES and add its folder to
    sandbox_workspace_write.writable_roots — never ~/.codex itself."""
    p = os.environ.get("SESSION_NOTES", "").strip()
    if p:
        return Path(os.path.expanduser(p))
    base = cwd or os.getcwd()
    return Path(base) / ".codex" / "session-notes.md"


def state_dir():
    d = Path(os.environ.get("CODEX_HOME", "").strip() or os.path.join(os.path.expanduser("~"), ".codex")) / "session-notes-state"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return d


def read_event():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except (ValueError, OSError):
        return {}


def emit(obj):
    sys.stdout.write(json.dumps(obj))
    sys.stdout.flush()


def age_minutes(path):
    try:
        return (time.time() - path.stat().st_mtime) / 60.0
    except OSError:
        return None


def session_state(session_id):
    f = state_dir() / ("%s.json" % "".join(c for c in (session_id or "unknown") if c.isalnum() or c in "-_")[:64])
    try:
        return f, json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return f, {}


def save_state(f, st):
    try:
        f.write_text(json.dumps(st), encoding="utf-8")
    except OSError:
        pass


def cmd_session_start(ev):
    p = notes_path(ev.get("cwd"))
    n = int(os.environ.get("SESSION_NOTES_HEAD_LINES") or 80)
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
              "No session-notes file exists yet at %s. Create it in your first tool-using turn "
              "(see the session-notes skill): tasks and status, decisions with reasons, files touched, open threads, "
              "with an 'Updated: <real clock>' line at the top." % p}})
        return
    head = "\n".join(lines[:n])
    more = " (%d more lines in the file)" % (len(lines) - n) if len(lines) > n else ""
    emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
          "Session notes from %s%s — read before starting, and keep this file current during the session:\n\n%s" % (p, more, head)}})


def cmd_pre_compact(ev):
    f, st = session_state(ev.get("session_id"))
    st["compact_ts"] = time.time()
    st["compact_trigger"] = ev.get("trigger") or "auto"
    st["compact_stale_min"] = age_minutes(notes_path(ev.get("cwd")))
    save_state(f, st)
    # no output: a compaction is never blocked


def cmd_stop(ev):
    if os.environ.get("SESSION_NOTES_GUARD", "").strip().lower() in ("off", "0", "false", "no"):
        return
    if ev.get("stop_hook_active"):
        return                                  # already continued once this turn
    p = notes_path(ev.get("cwd"))
    stale_min = float(os.environ.get("SESSION_NOTES_STALE_MIN") or 30)
    f, st = session_state(ev.get("session_id"))
    age = age_minutes(p)
    reason = None
    if age is None:
        reason = ("Before finishing: the session-notes file %s does not exist. Create it now (session-notes skill: "
                  "tasks and status, decisions with their reasons, files touched, open threads; 'Updated: <real clock>' "
                  "at the top), then give the one-line answer you were about to give." % p)
    elif st.get("compact_ts") and (st.get("compact_stale_min") or 0) > 10 and not st.get("compact_handled"):
        reason = ("A compaction (%s) ran while %s was %.0f minutes stale, so the summary may now be the only record "
                  "of what came before it. Write the durable parts into the notes file — decisions and reasons, "
                  "identifiers, files touched — update its date line, then finish." % (st.get("compact_trigger"), p, st.get("compact_stale_min") or 0))
        st["compact_handled"] = True
    elif age > stale_min:
        reason = ("Before finishing: %s was last updated %.0f minutes ago. Update it now — what was done this turn, "
                  "decisions with their reasons, files touched, what is open — and its 'Updated:' line, then finish "
                  "with one line saying the notes were updated." % (p, age))
    if reason:
        st["last_block_ts"] = time.time()
        save_state(f, st)
        emit({"decision": "block", "reason": reason})


def cmd_status():
    p = notes_path()
    age = age_minutes(p)
    print("notes file: %s" % p)
    print("exists: %s  age: %s" % (p.exists(), "%.0f min" % age if age is not None else "-"))
    print("stale after: %s min  guard: %s" % (os.environ.get("SESSION_NOTES_STALE_MIN") or 30,
                                            "off" if os.environ.get("SESSION_NOTES_GUARD", "").lower() in ("off", "0", "false", "no") else "on"))


def main(argv):
    sub = (argv[1] if len(argv) > 1 else "").strip().lower()
    if sub == "status":
        cmd_status()
        return 0
    ev = read_event()
    try:
        if sub == "session-start":
            cmd_session_start(ev)
        elif sub == "stop":
            cmd_stop(ev)
        elif sub == "pre-compact":
            cmd_pre_compact(ev)
        else:
            sys.stderr.write(__doc__)
            return 0
    except Exception as exc:  # a hook error must never take the session down
        sys.stderr.write("session_notes hook: %s\n" % exc)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
