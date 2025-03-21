# Casper

Casper is a GPU-accelerated audio transcription tool using Whisper via the faster-whisper library. It processes audio files organized in subfolders and generates structured transcription outputs.

## Features

- **GPU Acceleration**: Utilizes CUDA for fast transcription processing
- **Batch Processing**: Processes multiple audio files across hierarchical folder structures
- **Flexible Output**: Creates consolidated CSV files with transcriptions and metadata
- **Detailed Statistics**: Tracks processing time, accuracy, and performance metrics
- **Docker Support**: Simple deployment with Docker and GPU passthrough

## System Requirements

- NVIDIA GPU with CUDA support
- Docker with NVIDIA Container Toolkit (recommended)
- Python 3.8+
- PyTorch with CUDA support
- faster-whisper library

## Project Structure

```
casper/
├── data/                     # Data directory
│   ├── input/                # Input audio files organized in subfolders
│   │   └── <person_name>/    # Person-specific audio files
│   └── output/               # Generated transcriptions and statistics
├── transcriber.py            # Transcription engine using faster-whisper
├── pipeline.py               # Processing pipeline for batch transcription
├── main.py                   # Command-line interface
├── cleanup_output.sh         # Script to clean output directory
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── Makefile                  # Build and run automation
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation
```

## Quick Start with Make

```bash
# Setup directories and environment
make setup

# Build the Docker image
make build

# Run the transcription service with GPU support
make run-gpu

# Clean output directory
make clean
```

## Detailed Installation

### Option 1: Using Docker (Recommended)

1. **Install NVIDIA Driver and Docker**:
   ```bash
   # Run setup script to install NVIDIA Container Toolkit
   bash setup.sh
   ```

2. **Build and Run with Docker**:
   ```bash
   # Using make
   make build
   make run-gpu
   
   # Or using Docker Compose directly
   docker-compose build
   docker-compose run transcription-service --model large-v3-turbo --device cuda
   ```

### Option 2: Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create necessary directories
make data-dirs

# Run transcription
python main.py --input ./data/input --output ./data/output --model tiny
```

## Input Format

Place your audio files in subfolders within the `data/input` directory. Each subfolder typically represents a person or a category:

```
data/input/
├── person1/
│   ├── recording1.wav
│   └── recording2.opus
├── person2/
│   └── interview.wav
└── ...
```

Supported audio formats:
- WAV (.wav)
- OPUS (.opus) 
- MP3 (.mp3)
- M4A (.m4a)
- OGG (.ogg)
- FLAC (.flac)

## Output Format

The transcription service generates a structured output:

```
data/output/
├── master_transcription_log.csv      # High-level stats for all folders
├── person1/
│   ├── person1_transcriptions.csv    # All transcriptions for person1
│   └── person1_segments.json         # Detailed segment data
├── person2/
│   ├── person2_transcriptions.csv
│   └── person2_segments.json
└── ...
```

## Usage

### Using Make Commands

The project includes a Makefile to automate common tasks:

```bash
# Show available commands
make help

# Create directories and install dependencies
make setup

# Run with default (tiny) model
make run

# Run with specific model
make run MODEL=medium

# Run with GPU support
make run-gpu MODEL=large-v3-turbo

# Run locally (no Docker)
make run-local

# Clean output directory
make clean

# Remove all generated files and Docker images
make clean-all

# View Docker logs
make logs
```

### Command-Line Arguments

When running directly, the following options are available:

```bash
python main.py --input <input_dir> --output <output_dir> [OPTIONS]

Options:
  --model MODEL           Model size: tiny, base, small, medium, large-v1, large-v2, large-v3, large-v3-turbo
  --device DEVICE         Device to use: cuda, cpu
  --compute-type TYPE     Compute type: float16, float32, int8
  --skip-gpu-check        Skip GPU availability check
```

## Cleanup

To clean the output directory:

```bash
# Using Make
make clean

# Or using the script directly
./cleanup_output.sh
sudo ./cleanup_output.sh  # If you encounter permission issues
```

## Performance Considerations

- **Model Selection**: Larger models provide better accuracy but require more GPU memory and processing time
- **Batch Size**: Processing many files at once works well but watch GPU memory usage
- **GPU Memory**: The large-v3 model requires at least 8GB of VRAM

## Troubleshooting

If you encounter CUDA library issues like `libcudnn_ops_infer.so.8 not found`:

1. Use the Docker solution which includes all necessary libraries
2. Check that your CUDA and cuDNN libraries match the PyTorch version
3. Run `nvidia-smi` to confirm GPU is detected

## License

[Insert your license information here]