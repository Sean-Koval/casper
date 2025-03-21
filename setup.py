#!/usr/bin/env python3
"""
Casper setup script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="casper",
    version="1.0.0",
    author="Sean Koval",
    description="GPU-accelerated audio transcription tool using Whisper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "faster-whisper>=0.6.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "tqdm>=4.62.0",
    ],
    entry_points={
        "console_scripts": [
            "casper=casper.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
)
