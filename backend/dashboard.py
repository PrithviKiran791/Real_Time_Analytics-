import streamlit as st
import pandas as pd
from cassandra.cluster import Cluster
import time
import altair as alt
from datetime import datetime, timedelta

# Page config with custom theme
st.set_page_config(
    page_title="Real-Time Payment Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main background and typography */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom card styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }
    
    /* Header styling */
    h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 2rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    h2, h3 {
        color: #1e293b !important;
        font-weight: 700 !important;
    }
    
    /* Card containers */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* Dataframe styling */
    div[data-testid="stDataFrame"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    /* Status indicator */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    /* Payment method badges */
    .payment-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-credit { background: #dbeafe; color: #1e40af; }
    .badge-debit { background: #fef3c7; color: #92400e; }
    .badge-upi { background: #dcfce7; color: #166534; }
    .badge-wallet { background: #fce7f3; color: #831843; }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    
    /* Transaction highlight */
    .latest-transaction {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        font-weight: 600;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# --- CONNECT ---
@st.cache_resource
def get_session():
    try:
        cluster = Cluster(['127.0.0.1'], port=9042)
        session = cluster.connect()
        session.set_keyspace('payment_app')
        return session, cluster
    except Exception as e:
        st.error(f"Failed to connect to Cassandra: {e}")
        return None, None

session, cluster = get_session()

if session is None:
    st.stop()

# --- INITIALIZE SESSION STATE ---
if 'last_transaction_id' not in st.session_state:
    st.session_state.last_transaction_id = None
if 'transaction_count' not in st.session_state:
    st.session_state.transaction_count = 0

# --- HEADER ---
st.markdown("# 💳 Live Payment Monitor")

# --- TOP METRICS ---
metric_cols = st.columns(5)

with metric_cols[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="status-online"></span>', unsafe_allow_html=True)
    st.metric("System Status", "ONLINE", "Streaming")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("Database", "Cassandra", "Connected")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    total_transactions_metric = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    total_amount_metric = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[4]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    avg_transaction_metric = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN LAYOUT ---
left_col, right_col = st.columns([2, 3])

with left_col:
    # Spending by Category Chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📊 Spending by Category")
    category_chart_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Payment Method Distribution
    st.markdown('<div class="chart-container" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    st.subheader("💳 Payment Method Distribution")
    payment_chart_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    # Latest Transaction Highlight
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔴 Live Transaction Feed")
    latest_transaction_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transaction Feed Table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📜 Recent Transactions")
    update_time = st.empty()
    feed_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Section - Top Merchants
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.subheader("🏪 Top Merchants by Transaction Volume")
merchant_chart_placeholder = st.empty()
st.markdown('</div>', unsafe_allow_html=True)

# --- REFRESH LOOP ---
while True:
    try:
        # Get last 50 transactions for analysis
        rows = session.execute(
            "SELECT * FROM transactions_by_user WHERE user_id='User_1' LIMIT 50"
        )
        df = pd.DataFrame(list(rows))

        if not df.empty:
            # Update metrics
            current_count = len(df)
            total_spent = df['amount'].sum()
            avg_amount = df['amount'].mean()
            
            # Check for new transaction
            latest_txn_id = str(df['transaction_id'].iloc[0])
            if st.session_state.last_transaction_id != latest_txn_id:
                st.session_state.transaction_count += 1
                st.session_state.last_transaction_id = latest_txn_id
            
            with total_transactions_metric:
                st.metric(
                    "Total Transactions", 
                    f"{current_count}",
                    f"+{st.session_state.transaction_count} new"
                )
            
            with total_amount_metric:
                st.metric(
                    "Total Spent", 
                    f"${total_spent:,.2f}",
                    f"${df['amount'].iloc[0]:,.2f}"
                )
            
            with avg_transaction_metric:
                st.metric(
                    "Avg Transaction", 
                    f"${avg_amount:,.2f}",
                    f"{((avg_amount / total_spent * 100) if total_spent > 0 else 0):.1f}%"
                )
            
            # Latest Transaction Highlight
            latest = df.iloc[0]
            with latest_transaction_placeholder:
                st.markdown(f"""
                    <div class="latest-transaction">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 0.85rem; opacity: 0.9;">LATEST TRANSACTION</div>
                                <div style="font-size: 1.5rem; margin-top: 0.5rem;">${latest['amount']:,.2f}</div>
                                <div style="margin-top: 0.5rem; opacity: 0.95;">{latest['merchant']} • {latest['category']}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 0.85rem; opacity: 0.9;">{pd.to_datetime(latest['transaction_time']).strftime('%H:%M:%S')}</div>
                                <div style="margin-top: 0.5rem; background: rgba(255,255,255,0.2); padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;">
                                    {latest['payment_method']}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Transaction Feed Table
            with update_time:
                st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            display_df = df.head(15)[['transaction_time', 'merchant', 'category', 'amount', 'payment_method']].copy()
            display_df['transaction_time'] = pd.to_datetime(display_df['transaction_time']).dt.strftime('%H:%M:%S')
            display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
            display_df.columns = ['Time', 'Merchant', 'Category', 'Amount', 'Payment']
            
            with feed_placeholder:
                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True,
                    height=350
                )

        # Get Analytics Data
        rows_stats = session.execute("SELECT category, total_spent FROM spending_analytics")
        df_stats = pd.DataFrame(list(rows_stats))

        if not df_stats.empty:
            # Category Donut Chart
            category_chart = alt.Chart(df_stats).mark_arc(
                innerRadius=50,
                outerRadius=110,
                cornerRadius=5
            ).encode(
                theta=alt.Theta("total_spent:Q", stack=True),
                color=alt.Color(
                    "category:N",
                    scale=alt.Scale(scheme='category20'),
                    legend=alt.Legend(title="Categories", orient="right", titleFontSize=11, labelFontSize=10)
                ),
                tooltip=[
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("total_spent:Q", title="Total Spent", format="$,.0f")
                ]
            ).properties(height=280)
            
            with category_chart_placeholder:
                st.altair_chart(category_chart, use_container_width=True)

        # Payment Method Distribution
        if not df.empty:
            payment_counts = df['payment_method'].value_counts().reset_index()
            payment_counts.columns = ['payment_method', 'count']
            
            payment_chart = alt.Chart(payment_counts).mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8
            ).encode(
                x=alt.X("count:Q", title="Number of Transactions"),
                y=alt.Y("payment_method:N", title=None, sort='-x'),
                color=alt.Color(
                    "payment_method:N",
                    scale=alt.Scale(scheme='set2'),
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip("payment_method:N", title="Payment Method"),
                    alt.Tooltip("count:Q", title="Transactions")
                ]
            ).properties(height=220)
            
            with payment_chart_placeholder:
                st.altair_chart(payment_chart, use_container_width=True)

        # Top Merchants
        if not df.empty:
            merchant_stats = df.groupby('merchant').agg({
                'amount': ['sum', 'count']
            }).reset_index()
            merchant_stats.columns = ['merchant', 'total_amount', 'transaction_count']
            merchant_stats = merchant_stats.sort_values('total_amount', ascending=False).head(10)
            
            merchant_chart = alt.Chart(merchant_stats).mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8
            ).encode(
                x=alt.X("total_amount:Q", title="Total Spent ($)"),
                y=alt.Y("merchant:N", title=None, sort='-x'),
                color=alt.Color(
                    "total_amount:Q",
                    scale=alt.Scale(scheme='viridis'),
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip("merchant:N", title="Merchant"),
                    alt.Tooltip("total_amount:Q", title="Total Spent", format="$,.2f"),
                    alt.Tooltip("transaction_count:Q", title="Transactions")
                ]
            ).properties(height=300)
            
            with merchant_chart_placeholder:
                st.altair_chart(merchant_chart, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
    
    time.sleep(1)
    st.rerun()