import time
import sqlite3
import re
import os

# -----------------------------
# File Paths
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(BASE_DIR, "logs.db")
LOG_FILE = os.path.join(BASE_DIR, "data", "access.log")

# Regex pattern (matches Apache combined log format)
pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<time>.*?)\] "(?P<method>\w+) (?P<url>.*?)" (?P<status>\d+)'
)

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
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
    conn.commit()
    conn.close()

# -----------------------------
# Watcher Function
# -----------------------------
def watch_log():
    print("👀 Watching log file for changes:", LOG_FILE)
    with open(LOG_FILE, "r") as f:
        # Move to end of file
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)  # wait before checking again
                continue
            match = pattern.search(line)
            if match:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?)", tuple(match.groups()))
                conn.commit()
                conn.close()
                print("✅ New log entry added:", match.groups())

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    init_db()
    watch_log()
