#!/usr/bin/env python3
"""
Create a binary sample file for testing binary file transfers.

This script creates a small binary file that can be used to test
the file transfer system with non-text content.
"""

import os
from pathlib import Path

def create_binary_sample():
    """Create a small binary file with various byte values."""
    
    # Create some binary data
    binary_data = bytearray()
    
    # Add various byte patterns
    for i in range(256):
        binary_data.append(i)
    
    # Add some random-looking data
    binary_data.extend(b'\x89PNG\r\n\x1a\n')  # PNG header
    binary_data.extend(b'FAKE_PNG_DATA')
    binary_data.extend(b'\x00' * 100)  # Null bytes
    binary_data.extend(b'\xFF' * 50)   # High bytes
    
    # Write to file
    output_path = Path(__file__).parent / 'binary_sample.bin'
    with open(output_path, 'wb') as f:
        f.write(binary_data)
    
    print(f"Created binary sample file: {output_path}")
    print(f"File size: {len(binary_data)} bytes")
    return output_path

if __name__ == '__main__':
    create_binary_sample()