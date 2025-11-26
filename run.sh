@"
#!/usr/bin/env bash

# run.sh - start demo producer in background and streamlit in foreground
set -e

# Move to /app (WORKDIR in Dockerfile)
cd /app || exit 1

# Start the producer (demo.py) in background if it exists
if [ -f ./backend/demo.py ]; then
  echo "Starting demo producer..."
  python ./backend/demo.py & disown
else
  echo "WARNING: backend/demo.py not found — skipping producer start"
fi

# Start Streamlit dashboard in foreground (listen on all interfaces)
if [ -f ./backend/dashboard.py ]; then
  echo "Starting Streamlit dashboard..."
  python -m streamlit run ./backend/dashboard.py --server.port=8501 --server.address=0.0.0.0
else
  echo "ERROR: backend/dashboard.py not found — nothing to run"
  tail -f /dev/null
fi
"@ | Set-Content -Path .\run.sh -Encoding UTF8
