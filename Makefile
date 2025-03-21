# Casper - Audio Transcription Service Makefile
# --------------------------------------

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := casper
DATA_DIR := ./data
INPUT_DIR := $(DATA_DIR)/input
OUTPUT_DIR := $(DATA_DIR)/output
MODEL_SIZE := tiny

# Default goal
.PHONY: help
help:
	@echo "Casper - Audio Transcription Service"
	@echo "-----------------------------------"
	@echo "Available commands:"
	@echo ""
	@echo "  make help               - Show this help message"
	@echo "  make setup              - Create necessary directories and install dependencies"
	@echo "  make install            - Install Python dependencies"
	@echo "  make clean              - Clean output directory"
	@echo "  make build              - Build Docker image"
	@echo "  make run                - Run transcription service with Docker"
	@echo "  make run-local          - Run transcription service locally (without Docker)"
	@echo "  make run-gpu            - Run transcription service with GPU support"
	@echo "  make test-gpu           - Test GPU availability"
	@echo "  make stop               - Stop running Docker containers"
	@echo "  make logs               - View Docker container logs"
	@echo ""
	@echo "Advanced usage:"
	@echo ""
	@echo "  make run MODEL=large-v3-turbo     - Run with a specific model size"
	@echo "  make clean-all                    - Remove all generated files and Docker images"
	@echo ""

# Setup directories and environment
.PHONY: setup
setup: install data-dirs

# Create data directories
.PHONY: data-dirs
data-dirs:
	@echo "Creating data directories..."
	@mkdir -p $(INPUT_DIR) $(OUTPUT_DIR)
	@touch $(OUTPUT_DIR)/.gitkeep
	@echo "Done! Created input and output directories."

# Install dependencies
.PHONY: install
install:
	@echo "Installing Python dependencies..."
	@$(PIP) install -r requirements.txt
	@echo "Done!"

# Clean output directory
.PHONY: clean
clean:
	@echo "Cleaning output directory..."
	@./cleanup_output.sh $(OUTPUT_DIR) -y
	@echo "Done!"

# Full cleanup (output, Docker containers, images)
.PHONY: clean-all
clean-all: clean
	@echo "Removing Docker containers and images..."
	@$(DOCKER_COMPOSE) down --rmi all 2>/dev/null || true
	@$(DOCKER) rmi $(PROJECT_NAME) 2>/dev/null || true
	@echo "Done!"

# Build Docker image
.PHONY: build
build:
	@echo "Building Docker image..."
	@$(DOCKER_COMPOSE) build
	@echo "Done!"

# Run with Docker
.PHONY: run
run: data-dirs
	@echo "Running transcription service with Docker..."
	@$(DOCKER_COMPOSE) run transcription-service --model $(MODEL)

# Run with Docker and GPU
.PHONY: run-gpu
run-gpu: data-dirs
	@echo "Running transcription service with GPU support..."
	@$(DOCKER_COMPOSE) run transcription-service --model $(MODEL) --device cuda --compute-type float16

# Run locally without Docker
.PHONY: run-local
run-local: data-dirs
	@echo "Running transcription service locally..."
	@$(PYTHON) main.py --input $(INPUT_DIR) --output $(OUTPUT_DIR) --model $(MODEL)

# Test GPU availability
.PHONY: test-gpu
test-gpu:
	@echo "Testing GPU availability..."
	@$(PYTHON) gpu_test_basic.py

# Stop Docker containers
.PHONY: stop
stop:
	@echo "Stopping Docker containers..."
	@$(DOCKER_COMPOSE) down
	@echo "Done!"

# View Docker logs
.PHONY: logs
logs:
	@$(DOCKER_COMPOSE) logs -f

# Default model (can be overridden via command line)
MODEL ?= $(MODEL_SIZE)
