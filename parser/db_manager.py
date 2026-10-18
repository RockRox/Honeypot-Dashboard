"""
db_manager.py
SQLite schema creation and all database operations for the honeypot pipeline.
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.getenv("DB_PATH", "../data/honeypot.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # better concurrent read performance
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Create all tables if they don't exist."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with get_connection(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id        TEXT NOT NULL,
                timestamp       TEXT NOT NULL,
                src_ip          TEXT NOT NULL,
                src_port        INTEGER,
                session         TEXT,
                username        TEXT,
                password        TEXT,
                command         TEXT,
                success         INTEGER DEFAULT 0,
                raw             TEXT,
                created_at      TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT UNIQUE NOT NULL,
                src_ip          TEXT NOT NULL,
                start_time      TEXT,
                end_time        TEXT,
                duration_secs   REAL,
                commands_run    INTEGER DEFAULT 0,
                login_success   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS ip_intel (
                ip              TEXT PRIMARY KEY,
                country         TEXT,
                country_code    TEXT,
                region          TEXT,
                city            TEXT,
                isp             TEXT,
                org             TEXT,
                asn             TEXT,
                lat             REAL,
                lon             REAL,
                abuse_score     INTEGER DEFAULT 0,
                abuse_reports   INTEGER DEFAULT 0,
                last_seen       TEXT,
                is_tor          INTEGER DEFAULT 0,
                enriched_at     TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_events_ip        ON events(src_ip);
            CREATE INDEX IF NOT EXISTS idx_events_ts        ON events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_events_event_id  ON events(event_id);
        """)
    print(f"[db] Database initialised at {db_path}")


def insert_event(event: dict, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO events
                (event_id, timestamp, src_ip, src_port, session,
                 username, password, command, success, raw)
            VALUES
                (:event_id, :timestamp, :src_ip, :src_port, :session,
                 :username, :password, :command, :success, :raw)
        """, event)


def upsert_session(session: dict, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO sessions
                (session_id, src_ip, start_time, end_time,
                 duration_secs, commands_run, login_success)
            VALUES
                (:session_id, :src_ip, :start_time, :end_time,
                 :duration_secs, :commands_run, :login_success)
            ON CONFLICT(session_id) DO UPDATE SET
                end_time       = excluded.end_time,
                duration_secs  = excluded.duration_secs,
                commands_run   = excluded.commands_run,
                login_success  = excluded.login_success
        """, session)


def upsert_ip_intel(intel: dict, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO ip_intel
                (ip, country, country_code, region, city, isp, org,
                 asn, lat, lon, abuse_score, abuse_reports, last_seen,
                 is_tor, enriched_at)
            VALUES
                (:ip, :country, :country_code, :region, :city, :isp,
                 :org, :asn, :lat, :lon, :abuse_score, :abuse_reports,
                 :last_seen, :is_tor, :enriched_at)
            ON CONFLICT(ip) DO UPDATE SET
                abuse_score   = excluded.abuse_score,
                abuse_reports = excluded.abuse_reports,
                last_seen     = excluded.last_seen,
                enriched_at   = excluded.enriched_at
        """, intel)


def get_unenriched_ips(db_path: str = DB_PATH) -> list[str]:
    """Return IPs in events table that have no ip_intel row yet."""
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT DISTINCT e.src_ip
            FROM events e
            LEFT JOIN ip_intel i ON e.src_ip = i.ip
            WHERE i.ip IS NULL
        """).fetchall()
    return [r["src_ip"] for r in rows]


def get_stats(hours: int = 24, db_path: str = DB_PATH) -> dict:
    with get_connection(db_path) as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE timestamp >= datetime('now', ?)",
            (f"-{hours} hours",)
        ).fetchone()["n"]

        unique_ips = conn.execute(
            "SELECT COUNT(DISTINCT src_ip) AS n FROM events WHERE timestamp >= datetime('now', ?)",
            (f"-{hours} hours",)
        ).fetchone()["n"]

        top_country = conn.execute("""
            SELECT i.country, COUNT(*) AS n
            FROM events e
            JOIN ip_intel i ON e.src_ip = i.ip
            WHERE e.timestamp >= datetime('now', ?)
            GROUP BY i.country ORDER BY n DESC LIMIT 1
        """, (f"-{hours} hours",)).fetchone()

        top_credential = conn.execute("""
            SELECT username || '/' || password AS cred, COUNT(*) AS n
            FROM events
            WHERE event_id = 'cowrie.login.failed'
              AND username IS NOT NULL
              AND timestamp >= datetime('now', ?)
            GROUP BY cred ORDER BY n DESC LIMIT 1
        """, (f"-{hours} hours",)).fetchone()

    return {
        "total_attacks":   total,
        "unique_ips":      unique_ips,
        "top_country":     dict(top_country) if top_country else {},
        "top_credential":  dict(top_credential) if top_credential else {},
        "window_hours":    hours,
    }
