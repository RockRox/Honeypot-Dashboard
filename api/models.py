"""models.py — all database read queries used by the API routes."""
import sqlite3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../parser"))
from db_manager import get_connection, get_stats as _get_stats
from config import DB_PATH


def db():
    return get_connection(DB_PATH)


# ── /api/stats ────────────────────────────────────────────────────────────────

def get_stats(hours: int = 24) -> dict:
    return _get_stats(hours, DB_PATH)


# ── /api/attacks ─────────────────────────────────────────────────────────────

def get_attacks(hours: int = 24, page: int = 1, per_page: int = 50) -> dict:
    offset = (page - 1) * per_page
    with db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE timestamp >= datetime('now', ?)",
            (f"-{hours} hours",)
        ).fetchone()["n"]

        rows = conn.execute("""
            SELECT e.event_id, e.timestamp, e.src_ip, e.src_port,
                   e.username, e.password, e.command, e.success,
                   i.country, i.country_code, i.city, i.isp,
                   i.abuse_score, i.lat, i.lon
            FROM events e
            LEFT JOIN ip_intel i ON e.src_ip = i.ip
            WHERE e.timestamp >= datetime('now', ?)
            ORDER BY e.timestamp DESC
            LIMIT ? OFFSET ?
        """, (f"-{hours} hours", per_page, offset)).fetchall()

    return {
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "data":     [dict(r) for r in rows],
    }


# ── /api/top-ips ──────────────────────────────────────────────────────────────

def get_top_ips(hours: int = 24, limit: int = 10) -> list:
    with db() as conn:
        rows = conn.execute("""
            SELECT e.src_ip,
                   COUNT(*) AS attempts,
                   i.country, i.country_code, i.city, i.isp, i.asn,
                   i.abuse_score, i.abuse_reports, i.is_tor,
                   MAX(e.timestamp) AS last_seen
            FROM events e
            LEFT JOIN ip_intel i ON e.src_ip = i.ip
            WHERE e.timestamp >= datetime('now', ?)
            GROUP BY e.src_ip
            ORDER BY attempts DESC
            LIMIT ?
        """, (f"-{hours} hours", limit)).fetchall()
    return [dict(r) for r in rows]


# ── /api/commands ─────────────────────────────────────────────────────────────

def get_top_commands(hours: int = 24, limit: int = 20) -> list:
    with db() as conn:
        rows = conn.execute("""
            SELECT command, COUNT(*) AS count
            FROM events
            WHERE event_id IN ('cowrie.command.input', 'cowrie.command.failed')
              AND command IS NOT NULL
              AND command != ''
              AND timestamp >= datetime('now', ?)
            GROUP BY command
            ORDER BY count DESC
            LIMIT ?
        """, (f"-{hours} hours", limit)).fetchall()
    return [dict(r) for r in rows]


# ── /api/map-data ─────────────────────────────────────────────────────────────

def get_map_data(hours: int = 24) -> list:
    with db() as conn:
        rows = conn.execute("""
            SELECT i.ip, i.lat, i.lon, i.country, i.country_code,
                   i.city, i.abuse_score,
                   COUNT(e.id) AS attempts
            FROM ip_intel i
            JOIN events e ON i.ip = e.src_ip
            WHERE e.timestamp >= datetime('now', ?)
              AND i.lat != 0 AND i.lon != 0
            GROUP BY i.ip
        """, (f"-{hours} hours",)).fetchall()
    return [dict(r) for r in rows]


# ── /api/credentials ──────────────────────────────────────────────────────────

def get_top_credentials(hours: int = 24, limit: int = 15) -> dict:
    with db() as conn:
        usernames = conn.execute("""
            SELECT username, COUNT(*) AS count
            FROM events
            WHERE event_id IN ('cowrie.login.failed', 'cowrie.login.success')
              AND username IS NOT NULL
              AND timestamp >= datetime('now', ?)
            GROUP BY username ORDER BY count DESC LIMIT ?
        """, (f"-{hours} hours", limit)).fetchall()

        passwords = conn.execute("""
            SELECT password, COUNT(*) AS count
            FROM events
            WHERE event_id IN ('cowrie.login.failed', 'cowrie.login.success')
              AND password IS NOT NULL
              AND timestamp >= datetime('now', ?)
            GROUP BY password ORDER BY count DESC LIMIT ?
        """, (f"-{hours} hours", limit)).fetchall()

        combos = conn.execute("""
            SELECT username || '/' || password AS combo, COUNT(*) AS count
            FROM events
            WHERE event_id IN ('cowrie.login.failed', 'cowrie.login.success')
              AND username IS NOT NULL AND password IS NOT NULL
              AND timestamp >= datetime('now', ?)
            GROUP BY combo ORDER BY count DESC LIMIT ?
        """, (f"-{hours} hours", limit)).fetchall()

    return {
        "usernames": [dict(r) for r in usernames],
        "passwords": [dict(r) for r in passwords],
        "combos":    [dict(r) for r in combos],
    }


# ── /api/timeline ─────────────────────────────────────────────────────────────

def get_timeline(hours: int = 24) -> list:
    """Return attack counts grouped by hour."""
    with db() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m-%d %H:00', timestamp) AS hour,
                   COUNT(*) AS attacks,
                   COUNT(DISTINCT src_ip) AS unique_ips
            FROM events
            WHERE timestamp >= datetime('now', ?)
            GROUP BY hour
            ORDER BY hour ASC
        """, (f"-{hours} hours",)).fetchall()
    return [dict(r) for r in rows]
