FROM python:3.10-slim

# Install ffmpeg and libgl for opencv
RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model weights implicitly by calling it once, optional but good for cache
# (Skipped to avoid long build times during dev)

COPY . .

# Create data dir
RUN mkdir -p /app/data
