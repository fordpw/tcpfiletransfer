#!/usr/bin/env python3
"""
Example script to start the TCP file transfer server.

This script demonstrates how to programmatically start the server
with custom configuration.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from server.file_server import FileTransferServer

def main():
    # Configuration
    HOST = 'localhost'
    PORT = 8888
    RECEIVE_DIR = 'received_files'
    
    print("TCP File Transfer Server Example")
    print(f"Starting server on {HOST}:{PORT}")
    print(f"Files will be saved to: {RECEIVE_DIR}")
    print("-" * 50)
    
    # Create and start server
    server = FileTransferServer(HOST, PORT, RECEIVE_DIR)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == '__main__':
    main()