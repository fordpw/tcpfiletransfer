#!/usr/bin/env python3
"""
TCP File Transfer Client

A TCP client that sends files to a file transfer server.
"""

import socket
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import common modules
sys.path.append(str(Path(__file__).parent.parent))

from common.protocol import (
    pack_message, unpack_message, create_file_info_message,
    ProtocolError, MSG_FILE_DATA, MSG_FILE_END, MSG_ACK, MSG_ERROR,
    CHUNK_SIZE
)


class FileTransferClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
    
    def send_file(self, file_path):
        """Send a file to the server."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        filesize = file_path.stat().st_size
        filename = file_path.name
        
        print(f"Connecting to {self.host}:{self.port}...")
        
        try:
            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            
            print(f"Connected! Sending file: {filename} ({filesize} bytes)")
            
            # Send file info
            file_info_msg = create_file_info_message(filename, filesize)
            client_socket.send(file_info_msg)
            
            # Wait for acknowledgment
            msg_type, data = unpack_message(client_socket)
            if msg_type == MSG_ERROR:
                error_msg = data.decode('utf-8')
                raise ProtocolError(f"Server error: {error_msg}")
            elif msg_type != MSG_ACK:
                raise ProtocolError(f"Expected ACK, got: {msg_type}")
            
            print(f"Server ready: {data.decode('utf-8')}")
            
            # Send file data in chunks
            bytes_sent = 0
            with open(file_path, 'rb') as f:
                while bytes_sent < filesize:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # Send chunk
                    file_data_msg = pack_message(MSG_FILE_DATA, chunk)
                    client_socket.send(file_data_msg)
                    bytes_sent += len(chunk)
                    
                    # Wait for acknowledgment
                    msg_type, data = unpack_message(client_socket)
                    if msg_type == MSG_ERROR:
                        error_msg = data.decode('utf-8')
                        raise ProtocolError(f"Server error: {error_msg}")
                    elif msg_type == MSG_ACK:
                        ack_msg = data.decode('utf-8')
                        print(f"\r{ack_msg}", end='', flush=True)
                    else:
                        raise ProtocolError(f"Expected ACK, got: {msg_type}")
            
            # Send end of file message
            file_end_msg = pack_message(MSG_FILE_END, b'')
            client_socket.send(file_end_msg)
            
            # Wait for final acknowledgment
            msg_type, data = unpack_message(client_socket)
            if msg_type == MSG_ERROR:
                error_msg = data.decode('utf-8')
                raise ProtocolError(f"Server error: {error_msg}")
            elif msg_type == MSG_ACK:
                final_msg = data.decode('utf-8')
                print(f"\n{final_msg}")
            else:
                raise ProtocolError(f"Expected ACK, got: {msg_type}")
                
        except socket.error as e:
            print(f"\nConnection error: {e}")
            raise
        except ProtocolError as e:
            print(f"\nProtocol error: {e}")
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            raise
        finally:
            client_socket.close()
            print("Connection closed.")
    
    def send_multiple_files(self, file_paths):
        """Send multiple files to the server."""
        for file_path in file_paths:
            try:
                print(f"\n{'='*50}")
                self.send_file(file_path)
                print(f"Successfully sent: {file_path}")
            except Exception as e:
                print(f"Failed to send {file_path}: {e}")
                continue


def main():
    parser = argparse.ArgumentParser(description='TCP File Transfer Client')
    parser.add_argument('files', nargs='+', help='Files to send')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    
    args = parser.parse_args()
    
    client = FileTransferClient(args.host, args.port)
    
    if len(args.files) == 1:
        client.send_file(args.files[0])
    else:
        client.send_multiple_files(args.files)


if __name__ == '__main__':
    main()
