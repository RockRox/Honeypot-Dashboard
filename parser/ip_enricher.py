"""
ip_enricher.py
Enriches raw attacker IPs with geolocation (ip-api.com) and threat
intelligence (AbuseIPDB). Sends Telegram alerts for brand-new IPs.
Both external APIs have free tiers — no payment required.
"""

import os
import time
import requests
from datetime import datetime
from db_manager import get_unenriched_ips, upsert_ip_intel, DB_PATH

ABUSEIPDB_KEY   = os.getenv("ABUSEIPDB_API_KEY", "")
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT   = os.getenv("TELEGRAM_CHAT_ID", "")


# ── ip-api.com (free, no key needed, 45 req/min) ─────────────────────────────

def geolocate(ip: str) -> dict:
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,countryCode,regionName,city,isp,org,as,lat,lon"},
            timeout=5,
        )
        d = r.json()
        if d.get("status") == "success":
            return {
                "country":      d.get("country", "Unknown"),
                "country_code": d.get("countryCode", "??"),
                "region":       d.get("regionName", ""),
                "city":         d.get("city", ""),
                "isp":          d.get("isp", ""),
                "org":          d.get("org", ""),
                "asn":          d.get("as", ""),
                "lat":          d.get("lat", 0.0),
                "lon":          d.get("lon", 0.0),
            }
    except Exception as e:
        print(f"[geo] Error for {ip}: {e}")
    return {
        "country": "Unknown", "country_code": "??",
        "region": "", "city": "", "isp": "", "org": "",
        "asn": "", "lat": 0.0, "lon": 0.0,
    }


# ── AbuseIPDB (free tier: 1 000 checks/day) ──────────────────────────────────

def check_abuse(ip: str) -> dict:
    if not ABUSEIPDB_KEY:
        return {"abuse_score": 0, "abuse_reports": 0, "last_seen": "", "is_tor": 0}
    try:
        r = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": ABUSEIPDB_KEY, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
            timeout=5,
        )
        d = r.json().get("data", {})
        return {
            "abuse_score":   d.get("abuseConfidenceScore", 0),
            "abuse_reports": d.get("totalReports", 0),
            "last_seen":     d.get("lastReportedAt", ""),
            "is_tor":        1 if d.get("isTor") else 0,
        }
    except Exception as e:
        print(f"[abuse] Error for {ip}: {e}")
    return {"abuse_score": 0, "abuse_reports": 0, "last_seen": "", "is_tor": 0}


# ── Telegram alert ────────────────────────────────────────────────────────────

def send_telegram_alert(ip: str, geo: dict, abuse: dict) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    flag = _flag(geo.get("country_code", "??"))
    score = abuse.get("abuse_score", 0)
    severity = "🔴 HIGH" if score > 80 else "🟡 MEDIUM" if score > 30 else "🟢 LOW"
    msg = (
        f"🚨 *New Attacker Detected*\n"
        f"IP: `{ip}`\n"
        f"{flag} {geo.get('country', 'Unknown')} — {geo.get('city', '')}\n"
        f"ISP: {geo.get('isp', 'Unknown')}\n"
        f"Threat: {severity} (AbuseIPDB: {score}%)\n"
        f"Reports: {abuse.get('abuse_reports', 0)}"
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "Markdown"},
            timeout=5,
        )
    except Exception as e:
        print(f"[telegram] Failed: {e}")


def _flag(code: str) -> str:
    """Convert ISO country code to emoji flag."""
    try:
        return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())
    except Exception:
        return "🌐"


# ── Main enrichment loop ──────────────────────────────────────────────────────

def enrich_all(db_path: str = DB_PATH, delay: float = 1.5) -> int:
    """
    Fetch geolocation + threat intel for every IP not yet in ip_intel table.
    delay: seconds between requests to stay within free-tier rate limits.
    Returns count of IPs enriched.
    """
    ips = get_unenriched_ips(db_path)
    if not ips:
        print("[enricher] No new IPs to enrich.")
        return 0

    print(f"[enricher] Enriching {len(ips)} new IP(s)…")
    for ip in ips:
        geo   = geolocate(ip)
        abuse = check_abuse(ip)
        intel = {
            "ip":          ip,
            "enriched_at": datetime.utcnow().isoformat(),
            **geo,
            **abuse,
        }
        upsert_ip_intel(intel, db_path)
        send_telegram_alert(ip, geo, abuse)
        print(f"  [{ip}] {geo['country']} | abuse={abuse['abuse_score']}%")
        time.sleep(delay)

    print(f"[enricher] Done — enriched {len(ips)} IP(s).")
    return len(ips)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
    enrich_all()
