import streamlit as st
import pandas as pd
from cassandra.cluster import Cluster
import time
import altair as alt

st.set_page_config(page_title="Real-Time Payment Dashboard", layout="wide")

# --- CONNECT ---
@st.cache_resource
def get_session():
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect()
    session.set_keyspace('payment_app')
    return session

session = get_session()

# --- HEADER ---
st.title("💳 Live Payment Monitor")
col1, col2, col3 = st.columns(3)
col1.metric("System Status", "ONLINE", "Stable")
col2.metric("Database", "Cassandra", "Connected")

# --- LAYOUT ---
# Top Row: Metrics & Charts
chart_col, feed_col = st.columns([2, 3])

with chart_col:
    st.subheader("Spending by Category")
    chart_placeholder = st.empty()

with feed_col:
    st.subheader("Live Transaction Feed")
    feed_placeholder = st.empty()

# --- REFRESH LOOP ---
while True:
    # 1. Get Live Feed (Last 10 items)
    rows = session.execute("SELECT * FROM transactions_by_user WHERE user_id='User_1' LIMIT 10")
    df = pd.DataFrame(list(rows))

    if not df.empty:
        # Format for display
        df = df[['transaction_time', 'merchant', 'category', 'amount', 'payment_method']]
        df['transaction_time'] = pd.to_datetime(df['transaction_time']).dt.strftime('%H:%M:%S')
        
        with feed_placeholder.container():
            st.dataframe(df, hide_index=True, use_container_width=True)

    # 2. Get Analytics (Counters)
    rows_stats = session.execute("SELECT category, total_spent FROM spending_analytics")
    df_stats = pd.DataFrame(list(rows_stats))

    if not df_stats.empty:
        base = alt.Chart(df_stats).encode(theta=alt.Theta("total_spent", stack=True))
        pie = base.mark_arc(outerRadius=120).encode(
            color=alt.Color("category"),
            order=alt.Order("total_spent", sort="descending"),
            tooltip=["category", "total_spent"]
        )
        text = base.mark_text(radius=140).encode(
            text="total_spent",
            order=alt.Order("total_spent", sort="descending")
        )
        
        with chart_placeholder.container():
            st.altair_chart(pie + text, use_container_width=True)

    time.sleep(1)
    st.rerun()