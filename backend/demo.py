import csv
import time
import uuid
import random
import os
from datetime import datetime
from cassandra.cluster import Cluster

print("--- LIGHTWEIGHT REAL-TIME DEMO ---")

# --- CONFIGURATION ---
# UPDATE THIS to match where you saved the new file!
FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "transactions.csv")


# 1. Connect to Cassandra
print("[1/4] Connecting to Cassandra...")
session = None
cluster = None

while True:
    try:
        cluster = Cluster(['127.0.0.1'], port=9042)
        session = cluster.connect()
        print("      SUCCESS! Connected.")
        break
    except Exception as e:
        print("      ... Waiting for Cassandra ...")
        time.sleep(5)

# 2. Setup Schema (Reset Mode)
print("[2/4] Setting up Schema...")

# Create Keyspace
session.execute("CREATE KEYSPACE IF NOT EXISTS payment_app WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")
session.set_keyspace('payment_app')

# --- FORCE CLEANUP: Drop old tables so we can recreate them with new columns ---
try:
    session.execute("DROP TABLE IF EXISTS transactions_by_user")
    session.execute("DROP TABLE IF EXISTS spending_analytics") # Renamed from spending_by_user... to match new script
    print("      Old tables dropped (Cleanup complete).")
except Exception as e:
    print(f"      Warning during cleanup: {e}")

# Re-Create Table A: The Log (Now with payment_method!)
session.execute("""
    CREATE TABLE transactions_by_user (
        user_id text,
        transaction_time timestamp,
        transaction_id UUID,
        amount float,
        category text,
        merchant text,
        payment_method text,
        PRIMARY KEY ((user_id), transaction_time)
    ) WITH CLUSTERING ORDER BY (transaction_time DESC);
""")

# Re-Create Table B: Analytics
session.execute("""
    CREATE TABLE spending_analytics (
        category text,
        total_spent counter,
        PRIMARY KEY (category)
    );
""")
print("      New Schema Created Successfully!")

# 3. Load Data into Memory
print(f"[3/4] Loading '{FILE_PATH}'...")
if not os.path.exists(FILE_PATH):
    print(f"\n[ERROR] File not found at: {FILE_PATH}")
    print("Please fix the FILE_PATH line in the code!")
    exit()

all_transactions = []
with open(FILE_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_transactions.append(row)

print(f"      Loaded {len(all_transactions)} templates. Starting Infinite Stream...")

# 4. Infinite Stream Loop
print("\n[4/4] STREAMING LIVE (Press Ctrl+C to Stop)")
print("-" * 60)

# We use a fixed user for the demo so the dashboard fills up nicely
DEMO_USER_ID = "User_1"

try:
    while True:
        # Pick a random transaction from the file to simulate variety
        row = random.choice(all_transactions)
        
        # --- Real-Time Transformation ---
        # Ignore the old date in the CSV. Use NOW.
        transaction_time = datetime.now()
        
        t_id = uuid.uuid4()
        amount = float(row['amount'])
        category = row['category']
        merchant = row['merchant']
        pay_method = row['payment_method']

        # --- Insert into Cassandra ---
        
        # 1. Log the Transaction
        session.execute(
            """
            INSERT INTO transactions_by_user 
            (user_id, transaction_time, transaction_id, amount, category, merchant, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (DEMO_USER_ID, transaction_time, t_id, amount, category, merchant, pay_method)
        )
        
        # 2. Update Analytics (Counter)
        session.execute(
            "UPDATE spending_analytics SET total_spent = total_spent + %s WHERE category = %s",
            (int(amount), category)
        )

        # --- Log to Console ---
        print(f"[{transaction_time.strftime('%H:%M:%S')}] New {pay_method} txn: ${amount:6.2f} at {merchant} ({category})")
        
        # Wait 1 second before next transaction (Natural speed)
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nStream Stopped.")
    cluster.shutdown()