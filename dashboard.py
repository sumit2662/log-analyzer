import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# Database Connection
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(BASE_DIR, "logs.db")

def get_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()
    return df

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📊 Log Analyzer Dashboard")

df = get_data()

if df.empty:
    st.warning("No logs found in database. Run parser first.")
else:
    # Show raw table
    st.subheader("Log Entries")
    st.dataframe(df)

    # Status code distribution
    st.subheader("Status Code Distribution")
    fig = px.histogram(df, x="status", title="HTTP Status Codes")
    st.plotly_chart(fig)

    # Requests per IP
    st.subheader("Requests per IP")
    ip_counts = df["ip"].value_counts().reset_index()
    ip_counts.columns = ["ip", "count"]
    fig2 = px.bar(ip_counts, x="ip", y="count", title="Requests by IP")
    st.plotly_chart(fig2)

    # Alerts: IPs with >5 failed logins
    st.subheader("Suspicious Activity (401 Errors)")
    alerts = df[df["status"] == 401]["ip"].value_counts()
    alerts = alerts[alerts > 5]
    if not alerts.empty:
        st.error("⚠️ Suspicious IPs detected:")
        st.write(alerts)
    else:
        st.success("✅ No suspicious activity detected.")
