#!/usr/bin/env python3
"""
Casper - GPU-accelerated audio transcription tool
Main entry point for the transcription service
"""

import os
import argparse
import torch
from casper.utils.gpu import check_gpu
from casper.transcription.pipeline import TranscriptionPipeline

def main():
    """Main entry point for the transcription service"""
    parser = argparse.ArgumentParser(description='Transcribe audio files using faster-whisper')
    
    parser.add_argument('--input', type=str, required=True,
                        help='Input directory containing person folders with audio files')
    parser.add_argument('--output', type=str, required=True,
                        help='Output directory where transcription CSVs will be stored')
    parser.add_argument('--model', type=str, default='tiny',
                        choices=['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large-v3-turbo'],
                        help='Whisper model size (default: tiny)')
    parser.add_argument('--device', type=str, choices=['cuda', 'cpu'],
                        help='Device to use for inference (default: auto-detect)')
    parser.add_argument('--compute-type', type=str, choices=['float16', 'float32', 'int8'],
                        help='Compute type for the model (default: float16 for GPU, int8 for CPU)')
    parser.add_argument('--skip-gpu-check', action='store_true',
                        help='Skip GPU availability check')
    
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.exists(args.input):
        print(f"ERROR: Input directory '{args.input}' does not exist")
        return 1
    
    # Check GPU availability
    if not args.skip_gpu_check:
        gpu_available = check_gpu()
        
        # Auto-select device if not specified
        if args.device is None:
            args.device = "cuda" if gpu_available else "cpu"
            print(f"Auto-selected device: {args.device}")
    elif args.device is None:
        # If GPU check is skipped and no device specified, auto-detect
        args.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Auto-selected device: {args.device}")
    
    # Run the transcription pipeline
    pipeline = TranscriptionPipeline(
        input_dir=args.input,
        output_dir=args.output,
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type
    )
    
    pipeline.run()
    return 0

if __name__ == "__main__":
    exit(main())
