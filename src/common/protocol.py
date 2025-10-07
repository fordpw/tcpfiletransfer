"""
File transfer protocol definitions and utilities.
"""
import struct
import json
import os
from typing import Dict, Any, Optional

# Protocol constants
HEADER_SIZE = 8  # Size of the message length header
CHUNK_SIZE = 4096  # Size of file chunks to send
MAX_FILENAME_SIZE = 255  # Maximum filename length

# Message types
MSG_FILE_INFO = b'INFO'
MSG_FILE_DATA = b'DATA'
MSG_FILE_END = b'FEND'
MSG_ACK = b'ACK_'
MSG_ERROR = b'ERR_'


class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass


def pack_message(msg_type: bytes, data: bytes) -> bytes:
    """
    Pack a message with header containing message type and length.
    
    Format: [4 bytes msg_type][4 bytes data_length][data]
    """
    if len(msg_type) != 4:
        raise ProtocolError("Message type must be exactly 4 bytes")
    
    data_length = len(data)
    header = msg_type + struct.pack('!I', data_length)
    return header + data


def unpack_message(socket) -> tuple[bytes, bytes]:
    """
    Unpack a message from socket, returning (msg_type, data).
    """
    # Read header (8 bytes: 4 for msg_type, 4 for length)
    header = receive_all(socket, HEADER_SIZE)
    if len(header) != HEADER_SIZE:
        raise ProtocolError("Failed to receive complete header")
    
    msg_type = header[:4]
    data_length = struct.unpack('!I', header[4:])[0]
    
    # Read data
    data = receive_all(socket, data_length)
    if len(data) != data_length:
        raise ProtocolError("Failed to receive complete data")
    
    return msg_type, data


def receive_all(socket, size: int) -> bytes:
    """
    Receive exactly 'size' bytes from socket.
    """
    data = b''
    while len(data) < size:
        chunk = socket.recv(size - len(data))
        if not chunk:
            break
        data += chunk
    return data


def create_file_info_message(filename: str, filesize: int) -> bytes:
    """
    Create a file info message.
    """
    info = {
        'filename': filename,
        'filesize': filesize
    }
    data = json.dumps(info).encode('utf-8')
    return pack_message(MSG_FILE_INFO, data)


def parse_file_info_message(data: bytes) -> Dict[str, Any]:
    """
    Parse a file info message.
    """
    try:
        return json.loads(data.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ProtocolError(f"Failed to parse file info: {e}")


def create_ack_message(message: str = "OK") -> bytes:
    """
    Create an acknowledgment message.
    """
    return pack_message(MSG_ACK, message.encode('utf-8'))


def create_error_message(error: str) -> bytes:
    """
    Create an error message.
    """
    return pack_message(MSG_ERROR, error.encode('utf-8'))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.
    """
    # Remove any path separators and keep only the basename
    safe_name = os.path.basename(filename)
    
    # Remove any remaining dangerous characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ".-_")
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    # Limit length
    if len(safe_name) > MAX_FILENAME_SIZE:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:MAX_FILENAME_SIZE-len(ext)] + ext
    
    return safe_name