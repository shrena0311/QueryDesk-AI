import sqlite3
import streamlit as st
from sql_agent import ask

st.set_page_config(page_title="Query Desk", page_icon="🧾", layout="centered")

# ---------- pull a few quick stats for the sidebar, straight from the db ----------
conn = sqlite3.connect("store.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*), COUNT(DISTINCT Customer_ID), COUNT(DISTINCT Region) FROM orders")
total_rows, total_customers, total_regions = cur.fetchone()
cur.execute("SELECT MIN(Order_Date), MAX(Order_Date) FROM orders")
min_date, max_date = cur.fetchone()
conn.close()

# ---------- styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #12141A;
}

[data-testid="stSidebar"] {
    background: #0C0D11;
    border-right: 1px solid #262A33;
}

.desk-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    letter-spacing: 3px;
    color: #8F97A8;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.desk-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 30px;
    font-weight: 600;
    color: #F2EFE9;
    margin-bottom: 2px;
}

.desk-sub {
    color: #6B7280;
    font-size: 14px;
    margin-bottom: 22px;
}

.stat-box {
    font-family: 'IBM Plex Mono', monospace;
    background: #181B22;
    border: 1px solid #262A33;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
}

.stat-label {
    color: #6B7280;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stat-value {
    color: #E8B04B;
    font-size: 18px;
    font-weight: 600;
}

.query-line {
    font-family: 'IBM Plex Mono', monospace;
    color: #E8E6E1;
    background: #1B1E26;
    border-left: 2px solid #E8B04B;
    padding: 10px 14px;
    border-radius: 4px;
    margin: 14px 0 10px 0;
    font-size: 14.5px;
}

.receipt {
    background: #F7F3E9;
    color: #2B2A26;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14.5px;
    padding: 18px 20px 14px 20px;
    border-radius: 2px;
    margin-bottom: 4px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    position: relative;
}

.receipt::before {
    content: "";
    position: absolute;
    bottom: -8px;
    left: 0;
    right: 0;
    height: 8px;
    background:
        linear-gradient(-45deg, #F7F3E9 6px, transparent 0),
        linear-gradient(45deg, #F7F3E9 6px, transparent 0);
    background-position: bottom;
    background-repeat: repeat-x;
    background-size: 12px 8px;
}

.receipt-tag {
    font-size: 10.5px;
    letter-spacing: 2px;
    color: #8A6D3B;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.receipt-line {
    border-top: 1px dashed #C9C2AF;
    margin: 10px 0;
}

.sql-toggle summary {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #6B7280;
    cursor: pointer;
    margin-top: 14px;
    margin-bottom: 8px;
    list-style: none;
}

.sql-toggle summary::-webkit-details-marker {
    display: none;
}

.sql-toggle summary::before {
    content: "▸ ";
}

.sql-toggle[open] summary::before {
    content: "▾ ";
}

.sql-box {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    background: #0C0D11;
    color: #9FE6A0;
    border: 1px solid #262A33;
    border-radius: 6px;
    padding: 12px 14px;
    white-space: pre-wrap;
    margin-bottom: 24px;
}

[data-testid="stChatInput"] {
    border-top: 1px solid #262A33;
}
</style>
""", unsafe_allow_html=True)

# ---------- sidebar ----------
with st.sidebar:
    st.markdown('<div class="desk-header">Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="desk-title" style="font-size:20px;">Superstore Orders</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-box"><div class="stat-label">Rows</div><div class="stat-value">{total_rows:,}</div></div>
    <div class="stat-box"><div class="stat-label">Customers</div><div class="stat-value">{total_customers:,}</div></div>
    <div class="stat-box"><div class="stat-label">Regions</div><div class="stat-value">{total_regions}</div></div>
    <div class="stat-box"><div class="stat-label">Date range</div><div class="stat-value" style="font-size:13px;">{str(min_date)[:10]} to {str(max_date)[:10]}</div></div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="desk-header" style="margin-top:20px;">Try asking</div>', unsafe_allow_html=True)
    st.caption("Which category made the most sales?")
    st.caption("Top 5 customers by total spend")
    st.caption("Sales by region in 2017")

# ---------- main ----------
st.markdown('<div class="desk-header">Text-to-SQL Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="desk-title">Query Desk 🧾</div>', unsafe_allow_html=True)
st.markdown('<div class="desk-sub">Ask a question about the store\'s orders. The agent writes the SQL, runs it, and prints the answer.</div>', unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

for entry in st.session_state.history:
    st.markdown(f'<div class="query-line">&gt; {entry["question"]}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="receipt">
        <div class="receipt-tag">Query Desk · Answer</div>
        {entry["answer"]}
        <div class="receipt-line"></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <details class="sql-toggle">
        <summary>View SQL</summary>
        <div class="sql-box">{entry["sql"]}</div>
    </details>
    """, unsafe_allow_html=True)

question = st.chat_input("Ask about sales, customers, regions, products...")

if question:
    st.markdown(f'<div class="query-line">&gt; {question}</div>', unsafe_allow_html=True)
    with st.spinner("Writing SQL and running it..."):
        result = ask(question)

    st.markdown(f"""
    <div class="receipt">
        <div class="receipt-tag">Query Desk · Answer</div>
        {result["answer"]}
        <div class="receipt-line"></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <details class="sql-toggle">
        <summary>View SQL</summary>
        <div class="sql-box">{result["sql"]}</div>
    </details>
    """, unsafe_allow_html=True)

    st.session_state.history.append({
        "question": question,
        "answer": result["answer"],
        "sql": result["sql"],
    })
