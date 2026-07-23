import re
import sqlite3
import os

# -----------------------------
# File Paths (safe relative)
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(BASE_DIR, "logs.db")
LOG_FILE = os.path.join(BASE_DIR, "data", "access.log")

print("DB_FILE:", DB_FILE)
print("LOG_FILE:", LOG_FILE)

# Ensure data folder exists
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# Check log file
if not os.path.exists(LOG_FILE):
    print("❌ Log file not found:", LOG_FILE)
    exit()

# -----------------------------
# Connect to SQLite
# -----------------------------
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    ip TEXT,
    time TEXT,
    method TEXT,
    url TEXT,
    status INT
)
""")

# -----------------------------
# Regex Pattern (fixed)
# -----------------------------
pattern = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<time>.*?)\] "(?P<method>\w+) (?P<url>.*?)" (?P<status>\d+)')
# -----------------------------
# Parse Log File
# -----------------------------
with open(LOG_FILE, "r") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?)", tuple(match.groups()))

conn.commit()
conn.close()
print("✅ Logs parsed and stored successfully in", DB_FILE)

