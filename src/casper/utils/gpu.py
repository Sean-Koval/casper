"""
GPU utility functions for Casper
"""

import torch
import time

def check_gpu():
    """Check GPU availability and report details"""
    print("\n===== GPU INFORMATION =====")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available() and torch.cuda.device_count() > 0:
        print(f"CUDA version: {torch.version.cuda}")
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        
        # Check memory usage
        print(f"Total GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        print(f"Allocated GPU memory: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
        return True
    else:
        print("No CUDA-capable GPU detected!")
        return False

def benchmark_matrix_multiply(device='cuda'):
    """Run a simple matrix multiplication benchmark on CPU vs GPU"""
    print(f"\n===== PERFORMANCE TEST: Matrix Multiplication on {device.upper()} =====")
    
    # Create large random matrices
    matrix_size = 5000
    
    # Warm up
    x = torch.randn(matrix_size, matrix_size, device=device)
    y = torch.randn(matrix_size, matrix_size, device=device)
    
    # Run actual test
    start_time = time.time()
    
    # Force synchronization for accurate timing
    if device == 'cuda':
        torch.cuda.synchronize()
        
    # Matrix multiplication
    z = torch.matmul(x, y)
    
    # Force synchronization for accurate timing
    if device == 'cuda':
        torch.cuda.synchronize()
        
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"{device.upper()} computation time: {elapsed_time:.4f} seconds")
    return elapsed_time
