#!/usr/bin/env python3
"""
TCP File Transfer Server

A TCP server that receives files from clients over the network.
Files are saved to the received_files directory.
"""

import socket
import threading
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import common modules
sys.path.append(str(Path(__file__).parent.parent))

from common.protocol import (
    unpack_message, create_ack_message, create_error_message,
    parse_file_info_message, sanitize_filename, ProtocolError,
    MSG_FILE_INFO, MSG_FILE_DATA, MSG_FILE_END, CHUNK_SIZE
)


class FileTransferServer:
    def __init__(self, host='localhost', port=8888, receive_dir='received_files'):
        self.host = host
        self.port = port
        self.receive_dir = Path(receive_dir)
        self.running = False
        self.server_socket = None
        
        # Create receive directory if it doesn't exist
        self.receive_dir.mkdir(exist_ok=True)
    
    def start(self):
        """Start the server and listen for connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"Server listening on {self.host}:{self.port}")
            print(f"Files will be saved to: {self.receive_dir.absolute()}")
            print("Press Ctrl+C to stop the server")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New connection from {client_address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        """Handle a single client connection."""
        try:
            print(f"Handling client {client_address}")
            
            # Receive file info
            msg_type, data = unpack_message(client_socket)
            
            if msg_type != MSG_FILE_INFO:
                error_msg = create_error_message("Expected file info message")
                client_socket.send(error_msg)
                return
            
            file_info = parse_file_info_message(data)
            filename = sanitize_filename(file_info['filename'])
            filesize = file_info['filesize']
            
            print(f"Receiving file: {filename} ({filesize} bytes)")
            
            # Send acknowledgment
            ack_msg = create_ack_message("Ready to receive file")
            client_socket.send(ack_msg)
            
            # Prepare file path
            file_path = self.receive_dir / filename
            
            # If file already exists, add a number suffix
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_part = original_path.stem
                ext_part = original_path.suffix
                file_path = self.receive_dir / f"{name_part}_{counter}{ext_part}"
                counter += 1
            
            # Receive file data
            bytes_received = 0
            with open(file_path, 'wb') as f:
                while bytes_received < filesize:
                    try:
                        msg_type, data = unpack_message(client_socket)
                        
                        if msg_type == MSG_FILE_DATA:
                            f.write(data)
                            bytes_received += len(data)
                            
                            # Send acknowledgment for each chunk
                            progress = (bytes_received / filesize) * 100
                            ack_msg = create_ack_message(f"Received {bytes_received}/{filesize} bytes ({progress:.1f}%)")
                            client_socket.send(ack_msg)
                            
                        elif msg_type == MSG_FILE_END:
                            # File transfer complete
                            break
                        else:
                            raise ProtocolError(f"Unexpected message type: {msg_type}")
                            
                    except ProtocolError as e:
                        print(f"Protocol error: {e}")
                        error_msg = create_error_message(str(e))
                        client_socket.send(error_msg)
                        break
            
            if bytes_received == filesize:
                print(f"File received successfully: {file_path}")
                final_ack = create_ack_message(f"File '{filename}' received successfully")
                client_socket.send(final_ack)
            else:
                print(f"File transfer incomplete: {bytes_received}/{filesize} bytes")
                # Remove incomplete file
                if file_path.exists():
                    file_path.unlink()
                error_msg = create_error_message("File transfer incomplete")
                client_socket.send(error_msg)
                
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            try:
                error_msg = create_error_message(f"Server error: {str(e)}")
                client_socket.send(error_msg)
            except:
                pass
        finally:
            client_socket.close()
            print(f"Connection with {client_address} closed")


def main():
    parser = argparse.ArgumentParser(description='TCP File Transfer Server')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    parser.add_argument('--receive-dir', default='received_files', 
                       help='Directory to save received files (default: received_files)')
    
    args = parser.parse_args()
    
    server = FileTransferServer(args.host, args.port, args.receive_dir)
    server.start()


if __name__ == '__main__':
    main()