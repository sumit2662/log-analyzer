from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# -----------------------------
# Database Connection
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(BASE_DIR, "logs.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# Home / Health Check
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "endpoints": {
            "/": "API documentation and health check (this page)",
            "/search": "Search logs by ?ip=... and/or ?status=...",
            "/alerts": "IPs with more than 5 failed (401) login attempts"
        },
        "database": DB_FILE
    })

# -----------------------------
# Search Endpoint
# -----------------------------
@app.route("/search", methods=["GET"])
def search_logs():
    ip = request.args.get("ip")
    status = request.args.get("status")

    conn = get_db_connection()
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    if ip:
        query += " AND ip=?"
        params.append(ip)
    if status:
        query += " AND status=?"
        params.append(status)

    try:
        rows = conn.execute(query, params).fetchall()
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500
    conn.close()

    return jsonify([dict(row) for row in rows])

# -----------------------------
# Alerts Endpoint
# -----------------------------
@app.route("/alerts", methods=["GET"])
def alerts():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT ip, COUNT(*) as attempts
            FROM logs
            WHERE status=401
            GROUP BY ip
            HAVING attempts > 5
        """).fetchall()
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500
    conn.close()

    return jsonify([dict(row) for row in rows])

# -----------------------------
# Error Handlers
# -----------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": "Use /search or /alerts endpoints"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
