"""
scheduler.py
Runs the log parser and IP enricher on a fixed interval.
Start with: python scheduler.py
Or use the provided systemd service file.
"""

import os
import time
import schedule
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from log_parser import parse_logs
from ip_enricher import enrich_all


INTERVAL_MINUTES = int(os.getenv("PARSE_INTERVAL_MINUTES", "5"))


def run_pipeline():
    print(f"\n[scheduler] ── Pipeline run at {__import__('datetime').datetime.utcnow().isoformat()} ──")
    new_events = parse_logs()
    if new_events > 0:
        enrich_all()
    else:
        print("[scheduler] No new events — skipping enrichment.")


# Run once immediately on startup
run_pipeline()

# Then on schedule
schedule.every(INTERVAL_MINUTES).minutes.do(run_pipeline)
print(f"[scheduler] Running every {INTERVAL_MINUTES} minutes. Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(30)
