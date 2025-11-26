# Real-Time Analytics Dashboard for a Payment App
**Database Management Systems (DBMS) Project**

**Student:** Prithvi Kiran , Ojasvi Poonia & Pragoat🐐🐐🐐🔥🔥🔥 sindhole 
**Institute:** Ramaiah Institute of Technology
**Year:** 2025

---

## 📖 Project Overview
This project implements a scalable, real-time data pipeline designed to handle high-velocity payment transactions. Unlike traditional Relational Databases (RDBMS), which struggle with massive write loads, this system uses **Apache Cassandra** to ingest data with sub-millisecond latency.

The system simulates a live stream of user transactions (Credit Card, UPI, Wallets), processes them in real-time, and visualizes spending trends and fraud alerts on a live dashboard.

## 🏗️ Architecture
The system follows a standard Real-Time Big Data architecture:

1.  **Ingestion Layer (Producer):** A Python-based simulation script acts as the "Producer." It reads seed data, generates real-time timestamps, and pushes data asynchronously to the database.
2.  **Storage Layer (NoSQL):** **Apache Cassandra** (running via Docker). It uses a masterless architecture to ensure high availability and write throughput.
3.  **Analytics Layer:** Uses Cassandra `Counter` tables to perform server-side aggregation (e.g., Total Spend by Category) without expensive "Group By" queries.
4.  **Presentation Layer:** A **Streamlit** dashboard that polls the database every second to reflect the live state of the system.

---

## 🛠️ Technology Stack
* **Database:** Apache Cassandra (Docker Image: `cassandra:latest`)
* **Backend Logic:** Python 3.x
* **Drivers:** `cassandra-driver` (DataStax)
* **Visualization:** Streamlit, Altair, Pandas
* **Data Source:** Synthetic Transaction Dataset (`transactions.csv`)

---

## 💾 Database Schema Design
The schema is modeled specifically for **Query-First Design** (Cassandra Best Practice), avoiding Joins.

### 1. Transaction Log (`transactions_by_user`)
* **Purpose:** Stores the immutable history of every transaction.
* **Partition Key:** `user_id` (Keeps a user's data on the same node).
* **Clustering Key:** `transaction_time` (DESC) (Ensures the latest transactions are read first).

```sql
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
2. Real-Time Analytics (spending_analytics)
Purpose: Maintains live running totals.

Feature: Uses Cassandra's COUNTER data type for atomic updates. This eliminates the need for "Read-Modify-Write" cycles.

SQL

CREATE TABLE spending_analytics (
    category text,
    total_spent counter,
    PRIMARY KEY (category)
);
📂 Project Structure
Plaintext

DBMS_Project/
├── data/
│   └── transactions.csv      # Source dataset
├── backend/
│   ├── demo.py               # The Data Producer (Ingestion Pipeline)
│   ├── dashboard.py          # The Dashboard (Streamlit App)
│   └── requirements.txt      # Dependencies
├── README.md                 # Project Documentation
└── Dockerfile (Optional)     # Container config
🚀 How to Run the Project
Prerequisites
Docker Desktop (must be running).

Python 3.8+ installed.

Step 1: Start the Database
Run the Cassandra container using Docker:

Bash

docker run --name my-cassandra -p 9042:9042 -d cassandra:latest
(Wait 60 seconds for the database to initialize).

Step 2: Install Dependencies
Navigate to the project folder and install Python libraries:

Bash

pip install cassandra-driver streamlit pandas altair
Step 3: Start the Data Pipeline (Backend)
This script will create the Schema automatically and start generating data.

Bash

python demo.py
Leave this terminal running.

Step 4: Launch the Dashboard (Frontend)
Open a new terminal and run:

Bash

streamlit run dashboard.py
The dashboard will open automatically in your browser at http://localhost:8501.

💡 Key Features Implemented
Asynchronous Writes: The Python producer uses execute_async to simulate high-throughput ingestion without blocking the main thread.

Live Fraud Detection: Simple rule-based logic flags transactions over specific limits or suspicious categories in real-time.

Zero-Latency Aggregation: The "Spending by Category" pie chart uses pre-aggregated counters, ensuring the dashboard loads instantly even with millions of rows.

🔮 Future Scope
Integration with Apache Kafka for decoupled message queuing.

Implementation of TTL (Time To Live) to automatically expire old data and save storage.

Machine Learning integration for predictive fraud analysis.


---

### One Final Touch: `requirements.txt`
To make your project look even more complete, create one small file named `requirements.txt` in your folder and paste this inside:

```text
cassandra-driver==3.29.0
streamlit==1.31.0
pandas==2.2.0
altair==5.2.0