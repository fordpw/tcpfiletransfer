#!/usr/bin/env python3
"""
Example script to send files using the TCP file transfer client.

This script demonstrates how to programmatically send files
to the server.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from client.file_client import FileTransferClient

def main():
    # Configuration
    HOST = 'localhost'
    PORT = 8888
    
    # Files to send (modify this list to send different files)
    files_to_send = [
        'examples/sample.txt',  # Sample file included in the project
        # Add more files here as needed
    ]
    
    print("TCP File Transfer Client Example")
    print(f"Connecting to server at {HOST}:{PORT}")
    print(f"Files to send: {files_to_send}")
    print("-" * 50)
    
    # Create client
    client = FileTransferClient(HOST, PORT)
    
    # Send files
    for file_path in files_to_send:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        try:
            print(f"📤 Sending: {file_path}")
            client.send_file(file_path)
            print(f"✅ Successfully sent: {file_path}")
            
        except Exception as e:
            print(f"❌ Failed to send {file_path}: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("File transfer session complete!")

if __name__ == '__main__':
    main()