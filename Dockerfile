# Use development image with CUDA compiler
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

# System dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    libgl1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install requirements with CUDA 12.1 compatibility
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cu121

WORKDIR /app
COPY . .

# Create directories for input and output
RUN mkdir -p /data/input /data/output

# Install the package in development mode
RUN pip install -e .

# Make the script executable
RUN chmod +x /app/casper.py

# Set the entrypoint to run the transcription pipeline
ENTRYPOINT ["python3", "/app/casper.py", "--input", "/data/input", "--output", "/data/output"]

# Default command (can be overridden)
CMD ["--model", "tiny"]