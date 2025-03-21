#!/usr/bin/env python3
"""
Casper - Main entry point
This script provides a simple way to run the transcription service from the project root
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from casper.main import main

if __name__ == "__main__":
    sys.exit(main())
