# Real-Time Analytics – Setup & Run Guide

This README provides **everything needed** to run this project on any system — whether using **local Python + virtual environment** or **Docker Compose**. Share this with teammates so everyone can run the same environment with zero path issues.

---

# 📁 Project Structure

```
Real_Time_Analytics-/
│   README.md
│   requirements.txt
│   docker-compose.yml
│   Dockerfile
│   run.sh
│   dashboard.py      (if applicable)
│
├── backend/
│     demo.py
│     dashboard.py
│
├── data/
│     transactions.csv
│
└── venv/ (created locally, not in repo)
```

---

# ✅ Prerequisites (install before anything)

Your system must have:

* **Git**
* **Python 3.8+** (recommended: 3.11)
* **pip** (comes with Python)
* **Docker & Docker Compose** (for containerized setup)
* **VS Code** (optional, recommended)

Check versions:

```powershell
git --version
python --version
pip --version
docker --version
docker-compose --version
```

---

# 📥 0. Clone the Repository

```powershell
cd %USERPROFILE%\Desktop
git clone https://github.com/PrithviKiran791/Real_Time_Analytics-.git
cd Real_Time_Analytics-
```

---

# 🛠 1. Make the Backend Portable (Required)

Update `demo.py` to use **relative path**, not an absolute Windows path:

```python
import os
FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "transactions.csv")
```

This ensures the file works on *any* machine.

---

# OPTION A — Run Locally (Python + Virtual Environment)

This is ideal for development.

## 1. Create and activate virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Your prompt should now show `(venv)`.

## 2. Generate a correct requirements.txt

### Option A (recommended): auto-generate

```powershell
pip install pipreqs
pipreqs . --force
```

### Option B: use the starter file

Paste this into `requirements.txt`:

```
streamlit>=1.18.0
cassandra-driver>=3.25.0
pandas
numpy
plotly
matplotlib
```

## 3. Install dependencies

```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 4. Ensure Cassandra is running

If no Cassandra instance exists, run via Docker:

```powershell
docker run --name my-cassandra -p 9042:9042 -d cassandra:3.11
```

Check:

```powershell
docker ps
```

## 5. (Optional) Auto-create sample CSV

```powershell
$csv = "amount,category,merchant,payment_method`n12.34,groceries,StoreA,card`n45.00,transport,Taxi,cash"
Set-Content -Path ".\data\transactions.csv" -Value $csv
```

## 6. Start the real-time producer

```powershell
python .\backend\demo.py
```

## 7. Start the Streamlit dashboard (new terminal with venv active)

```powershell
python -m streamlit run .\backend\dashboard.py --server.port=8501 --server.address=0.0.0.0
```

## 8. Open the dashboard

```
http://localhost:8501
```

## 9. Stop and clean

```powershell
Ctrl + C
deactivate
```

---

# OPTION B — Full Docker Compose Setup (Recommended for Teammates)

This method guarantees identical environments for everyone.

Ensure the repo contains:

* Dockerfile
* docker-compose.yml
* run.sh

## 1. Build & start all services

```powershell
docker-compose up --build
```

This will start:

* **Cassandra** on port 9042
* **App container** running:

  * `demo.py` (real-time stream producer)
  * Streamlit dashboard on port 8501

## 2. Open dashboard

```
http://localhost:8501
```

## 3. View logs

```powershell
docker-compose logs -f app
docker-compose logs -f cassandra
```

## 4. Stop everything

```powershell
docker-compose down
```

To remove volumes:

```powershell
docker-compose down -v
```

---

# 🔧 Troubleshooting Guide

### ❌ Streamlit: command not found

Run with Python:

```powershell
python -m streamlit run backend\dashboard.py
```

### ❌ Cassandra connection error

Check if running:

```powershell
docker ps
```

If not, start:

```powershell
docker run --name my-cassandra -p 9042:9042 -d cassandra:3.11
```

### ❌ Port 9042 already in use

Find the container:

```powershell
docker ps
```

Stop it:

```powershell
docker stop <container_id>
```

### ❌ CSV not found

Check path resolution:

```python
import os
print(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "transactions.csv")))
```

Make sure file exists in `/data`.

### ❌ Missing packages

Add package to requirements:

```
PACKAGE_NAME
```

Then reinstall:

```powershell
pip install -r requirements.txt
```

---

# 📌 Suggested README Lines for Teammates (copy/paste)

```
1. Clone repo
2. python -m venv venv && .\venv\Scripts\activate
3. pip install -r requirements.txt
4. docker run -p 9042:9042 -d cassandra:3.11
5. python backend\demo.py
6. python -m streamlit run backend\dashboard.py
7. Open http://localhost:8501
```

---

# 🎯 Summary

This README gives:

* ✔ Environment setup (Python + Docker)
* ✔ How to install dependencies
* ✔ How to start Cassandra
* ✔ How to run the demo producer
* ✔ How to run the Streamlit dashboard
* ✔ Relative path handling (portable across systems)
* ✔ Troubleshooting instructions

Your teammates can now run this project on *any system* with zero modification.

If you want, I can also:

* Generate a polished architecture diagram
* Add badges (build, Docker, Python version)
* Add screenshots of the dashboard
* Add dataset documentation

Just tell me!
