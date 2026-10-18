"""app.py — Flask application entry point."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../parser"))

from flask import Flask
from flask_cors import CORS
from routes import bp
from config import DEBUG, PORT
from db_manager import init_db
from config import DB_PATH

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(bp)


@app.after_request
def add_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


if __name__ == "__main__":
    init_db(DB_PATH)
    print(f"[api] Starting Flask on port {PORT} (debug={DEBUG})")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
