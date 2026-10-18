"""
log_parser.py
Reads Cowrie JSON log files, extracts relevant events, and writes them to SQLite.
Tracks a cursor file so it never re-processes the same lines.
"""

import json
import os
import glob
from datetime import datetime
from db_manager import init_db, insert_event, upsert_session, get_connection, DB_PATH

COWRIE_LOG_PATH = os.getenv("COWRIE_LOG_PATH", "/home/cowrie/cowrie/var/log/cowrie/")
CURSOR_FILE     = os.path.join(os.path.dirname(__file__), ".parse_cursor.json")

# Event IDs we care about
TRACKED_EVENTS = {
    "cowrie.session.connect",
    "cowrie.session.closed",
    "cowrie.login.success",
    "cowrie.login.failed",
    "cowrie.command.input",
    "cowrie.command.failed",
    "cowrie.session.file_download",
}


# ── Cursor management ─────────────────────────────────────────────────────────

def load_cursor() -> dict:
    if os.path.exists(CURSOR_FILE):
        with open(CURSOR_FILE) as f:
            return json.load(f)
    return {}


def save_cursor(cursor: dict) -> None:
    with open(CURSOR_FILE, "w") as f:
        json.dump(cursor, f)


# ── Event normalisation ───────────────────────────────────────────────────────

def normalise(raw: dict) -> dict | None:
    """Extract a flat dict from a raw Cowrie JSON event. Returns None to skip."""
    eid = raw.get("eventid", "")
    if eid not in TRACKED_EVENTS:
        return None

    return {
        "event_id":  eid,
        "timestamp": raw.get("timestamp", datetime.utcnow().isoformat()),
        "src_ip":    raw.get("src_ip", "0.0.0.0"),
        "src_port":  raw.get("src_port"),
        "session":   raw.get("session"),
        "username":  raw.get("username"),
        "password":  raw.get("password"),
        "command":   raw.get("input") or raw.get("url"),
        "success":   1 if eid == "cowrie.login.success" else 0,
        "raw":       json.dumps(raw),
    }


# ── Session aggregation ───────────────────────────────────────────────────────

def build_sessions(events: list[dict]) -> dict:
    """Aggregate events into session records keyed by session_id."""
    sessions: dict[str, dict] = {}
    for ev in events:
        sid = ev.get("session")
        if not sid:
            continue
        if sid not in sessions:
            sessions[sid] = {
                "session_id":    sid,
                "src_ip":        ev["src_ip"],
                "start_time":    ev["timestamp"],
                "end_time":      ev["timestamp"],
                "duration_secs": 0.0,
                "commands_run":  0,
                "login_success": 0,
            }
        s = sessions[sid]
        if ev["timestamp"] < s["start_time"]:
            s["start_time"] = ev["timestamp"]
        if ev["timestamp"] > s["end_time"]:
            s["end_time"] = ev["timestamp"]
        if ev["event_id"] == "cowrie.command.input":
            s["commands_run"] += 1
        if ev["event_id"] == "cowrie.login.success":
            s["login_success"] = 1
    return sessions


# ── Main parse loop ───────────────────────────────────────────────────────────

def parse_logs(log_path: str = COWRIE_LOG_PATH, db_path: str = DB_PATH) -> int:
    """
    Parse all cowrie.json* log files, skipping already-processed lines.
    Returns the number of new events inserted.
    """
    init_db(db_path)
    cursor   = load_cursor()
    new_total = 0

    log_files = sorted(glob.glob(os.path.join(log_path, "cowrie.json*")))
    if not log_files:
        print(f"[parser] No log files found at {log_path}")
        return 0

    for filepath in log_files:
        filename      = os.path.basename(filepath)
        lines_done    = cursor.get(filename, 0)
        new_events    = []

        with open(filepath, "r", errors="replace") as f:
            for idx, line in enumerate(f):
                if idx < lines_done:
                    continue
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                    ev  = normalise(raw)
                    if ev:
                        new_events.append(ev)
                except json.JSONDecodeError:
                    pass
            cursor[filename] = idx + 1  # save position after last line read

        if new_events:
            for ev in new_events:
                insert_event(ev, db_path)
            sessions = build_sessions(new_events)
            for s in sessions.values():
                upsert_session(s, db_path)
            new_total += len(new_events)
            print(f"[parser] {filename}: +{len(new_events)} events, "
                  f"{len(sessions)} sessions")

    save_cursor(cursor)
    print(f"[parser] Done. Total new events this run: {new_total}")
    return new_total


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
    parse_logs()
