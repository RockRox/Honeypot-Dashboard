"""config.py — centralised configuration loaded from .env"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

API_KEY = os.getenv("API_KEY", "dev_key_change_me")
DB_PATH = os.getenv("DB_PATH", "../data/honeypot.db")
DEBUG   = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT    = int(os.getenv("PORT", "5000"))
