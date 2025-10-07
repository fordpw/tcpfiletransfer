#!/usr/bin/env python3
"""
Server integration module for GUI

Provides functions to handle server operations within the GUI context.
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from common.protocol import (
    unpack_message, create_ack_message, create_error_message,
    parse_file_info_message, sanitize_filename, ProtocolError,
    MSG_FILE_INFO, MSG_FILE_DATA, MSG_FILE_END
)


def handle_client_connection(client_socket, client_address, save_dir, callback=None):
    """
    Handle a single client connection for GUI server.
    
    Args:
        client_socket: The client socket
        client_address: Client address tuple
        save_dir: Path to save received files
        callback: Optional callback function for status messages
    """
    def log_message(msg):
        if callback:
            callback(msg)
        else:
            print(msg)
    
    try:
        log_message(f"Handling client {client_address}")
        
        # Receive file info
        msg_type, data = unpack_message(client_socket)
        
        if msg_type != MSG_FILE_INFO:
            error_msg = create_error_message("Expected file info message")
            client_socket.send(error_msg)
            return
        
        file_info = parse_file_info_message(data)
        filename = sanitize_filename(file_info['filename'])
        filesize = file_info['filesize']
        
        log_message(f"Receiving file: {filename} ({filesize} bytes)")
        
        # Send acknowledgment
        ack_msg = create_ack_message("Ready to receive file")
        client_socket.send(ack_msg)
        
        # Prepare file path
        file_path = Path(save_dir) / filename
        
        # If file already exists, add a number suffix
        counter = 1
        original_path = file_path
        while file_path.exists():
            name_part = original_path.stem
            ext_part = original_path.suffix
            file_path = Path(save_dir) / f"{name_part}_{counter}{ext_part}"
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
                    log_message(f"Protocol error: {e}")
                    error_msg = create_error_message(str(e))
                    client_socket.send(error_msg)
                    break
        
        if bytes_received == filesize:
            log_message(f"File received successfully: {file_path}")
            final_ack = create_ack_message(f"File '{filename}' received successfully")
            client_socket.send(final_ack)
        else:
            log_message(f"File transfer incomplete: {bytes_received}/{filesize} bytes")
            # Remove incomplete file
            if file_path.exists():
                file_path.unlink()
            error_msg = create_error_message("File transfer incomplete")
            client_socket.send(error_msg)
            
    except Exception as e:
        log_message(f"Error handling client {client_address}: {e}")
        try:
            error_msg = create_error_message(f"Server error: {str(e)}")
            client_socket.send(error_msg)
        except:
            pass
    finally:
        client_socket.close()
        log_message(f"Connection with {client_address} closed")