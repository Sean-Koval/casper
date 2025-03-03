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

CMD ["python3", "infer.py"]