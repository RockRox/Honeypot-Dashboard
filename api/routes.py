"""routes.py — Flask blueprint with all honeypot API endpoints."""
from flask import Blueprint, jsonify, request, g
from functools import wraps
from config import API_KEY
import models

bp = Blueprint("api", __name__, url_prefix="/api")


# ── Auth middleware ───────────────────────────────────────────────────────────

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorised — provide X-API-Key header"}), 401
        return f(*args, **kwargs)
    return wrapper


def hours_param(default: int = 24) -> int:
    try:
        v = int(request.args.get("hours", default))
        return max(1, min(v, 720))  # clamp to 1h–30d
    except ValueError:
        return default


# ── Endpoints ─────────────────────────────────────────────────────────────────

@bp.get("/stats")
@require_api_key
def stats():
    """Aggregate counts for the given time window."""
    return jsonify(models.get_stats(hours_param()))


@bp.get("/attacks")
@require_api_key
def attacks():
    """Paginated list of raw attack events."""
    page     = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(int(request.args.get("per_page", 50)), 200))
    return jsonify(models.get_attacks(hours_param(), page, per_page))


@bp.get("/top-ips")
@require_api_key
def top_ips():
    """Most active attacker IPs with threat intelligence."""
    limit = max(1, min(int(request.args.get("limit", 10)), 100))
    return jsonify(models.get_top_ips(hours_param(), limit))


@bp.get("/commands")
@require_api_key
def commands():
    """Most common commands entered by attackers post-login."""
    limit = max(1, min(int(request.args.get("limit", 20)), 100))
    return jsonify(models.get_top_commands(hours_param(), limit))


@bp.get("/map-data")
@require_api_key
def map_data():
    """GeoJSON-ready attack origin coordinates with attempt counts."""
    return jsonify(models.get_map_data(hours_param()))


@bp.get("/credentials")
@require_api_key
def credentials():
    """Top usernames, passwords, and username/password combos tried."""
    return jsonify(models.get_top_credentials(hours_param()))


@bp.get("/timeline")
@require_api_key
def timeline():
    """Attack volume grouped by hour for the time window."""
    return jsonify(models.get_timeline(hours_param()))


@bp.get("/health")
def health():
    """Health check — no auth required."""
    return jsonify({"status": "ok"})
