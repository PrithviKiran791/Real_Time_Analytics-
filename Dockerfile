# Dockerfile - application image for Streamlit dashboard + demo producer
FROM python:3.11-slim


# System deps for building some wheels (cassandra-driver may require build deps)
RUN apt-get update \
&& apt-get install -y --no-install-recommends \
build-essential \
libc6-dev \
libffi-dev \
libssl-dev \
git \
&& rm -rf /var/lib/apt/lists/*


# Create app directory
WORKDIR /app


# Copy only what we need first (better caching)
COPY requirements.txt /app/requirements.txt


# Install Python deps
RUN pip install --upgrade pip setuptools wheel \
&& pip install --no-cache-dir -r /app/requirements.txt


# Copy project
COPY . /app


# Expose Streamlit port
EXPOSE 8501


# Default environment
ENV PYTHONUNBUFFERED=1


# Default command: run both demo producer and streamlit using a simple script.
# We provide a small supervisor script inside the image (see run.sh below) that
# starts both processes and keeps the container alive.
COPY ./run.sh /app/run.sh
RUN chmod +x /app/run.sh


CMD ["/app/run.sh"]