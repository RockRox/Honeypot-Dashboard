# Architecture & Deployment Guide

## System Overview

```
Internet
   │
   ▼
Oracle Cloud VM (Ubuntu 22.04, Always Free)
   │
   ├── iptables NAT
   │     port 22  → 2222  (SSH honeypot)
   │     port 23  → 2223  (Telnet honeypot)
   │
   ├── Cowrie Honeypot (port 2222/2223)
   │     └── writes → /home/cowrie/cowrie/var/log/cowrie/cowrie.json
   │
   ├── Python Scheduler (cron every 5 min)
   │     ├── log_parser.py   → reads cowrie.json, writes SQLite
   │     └── ip_enricher.py  → enriches new IPs via ip-api.com + AbuseIPDB
   │                           sends Telegram alerts for new attackers
   │
   └── Flask API (port 5000)
         └── 7 REST endpoints → served to React dashboard

Vercel (free CDN)
   └── React dashboard → fetches from Flask API
```

## Oracle Cloud Setup

### 1. Create Always-Free VM

- Shape: VM.Standard.E2.1.Micro
- Image: Canonical Ubuntu 22.04
- Region: Mumbai (ap-mumbai-1) or Hyderabad (ap-hyderabad-1)
- Public IP: enabled

### 2. Security List (Oracle firewall)

Open these ingress ports in your VCN Security List:

| Port | Protocol | Purpose |
|------|----------|---------|
| 22   | TCP      | Your real SSH (keep this) |
| 2222 | TCP      | Cowrie SSH honeypot |
| 2223 | TCP      | Cowrie Telnet honeypot |
| 5000 | TCP      | Flask API |

> After Cowrie is running, optionally change your real SSH to port 2222 and expose port 22 purely to the honeypot. This is more realistic but riskier — only do this if you're comfortable.

### 3. Run setup scripts

```bash
# 1. Connect to your VM
ssh -i honeypot-key.pem ubuntu@YOUR_PUBLIC_IP

# 2. Clone the project
git clone https://github.com/YOUR_USERNAME/honeypot-dashboard.git
cd honeypot-dashboard

# 3. Set up Cowrie
chmod +x scripts/setup_cowrie.sh
./scripts/setup_cowrie.sh

# 4. Set up iptables
chmod +x scripts/setup_iptables.sh
sudo ./scripts/setup_iptables.sh

# 5. Configure environment
cp .env.example .env
nano .env   # set your API_KEY and optional AbuseIPDB key

# 6. Install Python deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. Initialise DB and start scheduler
python parser/scheduler.py &

# 8. Start Flask API
cd api && python app.py &
```

## Vercel Deployment (Frontend)

```bash
cd dashboard
npm install
npm run build
# Deploy via Vercel CLI or connect GitHub repo to vercel.com
```

Set these environment variables in Vercel:
- `VITE_API_URL` = your Oracle Cloud VM's public IP or domain
- `VITE_API_KEY` = same key as in your .env

## Free API Keys

| Service | URL | Free Tier |
|---------|-----|-----------|
| AbuseIPDB | https://www.abuseipdb.com/register | 1,000 checks/day |
| ip-api.com | No registration needed | 45 req/min |
| Telegram Bot | @BotFather on Telegram | Free |

## Estimated Resources Used

On the Oracle Always-Free VM:
- Cowrie: ~50MB RAM, minimal CPU
- Flask API: ~80MB RAM
- Scheduler: ~60MB RAM
- SQLite DB: grows ~5MB/week under normal attack load
- Total: well within the 1GB RAM limit
