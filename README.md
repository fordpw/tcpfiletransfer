# TCP File Transfer

A simple, secure TCP-based file transfer system that allows you to send and receive files over the internet. The system consists of a server that receives files and a client that sends files.

## Features

- **Simple Protocol**: Custom lightweight protocol for reliable file transfers
- **Progress Tracking**: Real-time progress updates during file transfers
- **Multiple File Support**: Send multiple files in a single session
- **Error Handling**: Robust error handling and recovery
- **Security**: Filename sanitization to prevent directory traversal attacks
- **Concurrent Connections**: Server supports multiple simultaneous client connections
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Project Structure

```
tcp-file-transfer/
├── src/
│   ├── server/
│   │   └── file_server.py       # TCP server implementation
│   ├── client/
│   │   └── file_client.py       # TCP client implementation
│   └── common/
│       ├── __init__.py
│       └── protocol.py          # Shared protocol definitions
├── examples/
│   ├── start_server.py          # Example server startup script
│   ├── send_file.py            # Example client usage script
│   └── sample.txt              # Sample file for testing
├── received_files/             # Directory where server saves received files
└── README.md
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd tcp-file-transfer
   ```

2. **Requirements:**
   - Python 3.6 or higher
   - No additional dependencies required (uses only Python standard library)

## Usage

### Starting the Server

The server listens for incoming connections and saves received files to a specified directory.

```bash
# Basic usage (listens on localhost:8888)
python src/server/file_server.py

# Custom host and port
python src/server/file_server.py --host 0.0.0.0 --port 9999

# Custom receive directory
python src/server/file_server.py --receive-dir /path/to/save/files
```

**Server Options:**
- `--host`: Server host address (default: localhost)
- `--port`: Server port number (default: 8888)
- `--receive-dir`: Directory to save received files (default: received_files)

**Example Output:**
```
Server listening on localhost:8888
Files will be saved to: C:\Users\user\projects\tcp-file-transfer\received_files
Press Ctrl+C to stop the server
New connection from ('127.0.0.1', 54321)
Receiving file: document.pdf (1048576 bytes)
File received successfully: received_files\document.pdf
```

### Sending Files (Client)

The client connects to a server and sends one or more files.

```bash
# Send a single file
python src/client/file_client.py file1.txt

# Send multiple files
python src/client/file_client.py file1.txt file2.pdf file3.jpg

# Connect to remote server
python src/client/file_client.py --host 192.168.1.100 --port 9999 file.txt
```

**Client Options:**
- `--host`: Server host address (default: localhost)
- `--port`: Server port number (default: 8888)
- `files`: One or more files to send (required)

**Example Output:**
```
==================================================
Connecting to localhost:8888...
Connected! Sending file: document.pdf (1048576 bytes)
Server ready: Ready to receive file
Received 1048576/1048576 bytes (100.0%)
File 'document.pdf' received successfully
Connection closed.
Successfully sent: document.pdf
```

## Protocol Details

The system uses a custom binary protocol for reliable file transfers:

### Message Format
```
[4 bytes: Message Type][4 bytes: Data Length][Variable: Data]
```

### Message Types
- `FINFO`: File information (filename and size)
- `FDATA`: File data chunk
- `FEND`: End of file transfer
- `ACK`: Acknowledgment
- `ERR`: Error message

### Transfer Flow
1. Client connects to server
2. Client sends `FINFO` with filename and file size
3. Server responds with `ACK` if ready
4. Client sends file data in `FDATA` chunks
5. Server acknowledges each chunk with `ACK`
6. Client sends `FEND` when complete
7. Server sends final `ACK` confirmation

## Security Features

- **Filename Sanitization**: Server sanitizes filenames to prevent directory traversal attacks
- **Path Validation**: Only basenames are used, paths are stripped
- **File Collision Handling**: Duplicate filenames get numbered suffixes
- **Error Handling**: Incomplete transfers are cleaned up automatically

## Examples

### Running the Server in the Background

```bash
# Start server on all interfaces
python src/server/file_server.py --host 0.0.0.0 --port 8888
```

### Sending Files Over the Internet

```bash
# Send to remote server
python src/client/file_client.py --host example.com --port 8888 important_file.pdf
```

### Batch File Transfer

```bash
# Send all images in current directory
python src/client/file_client.py --host server.example.com *.jpg *.png
```

## Troubleshooting

### Connection Issues
- **"Connection refused"**: Make sure the server is running and listening on the correct port
- **"Connection timeout"**: Check firewall settings and network connectivity
- **"Address already in use"**: Another process is using the port, try a different port

### File Transfer Issues
- **"File not found"**: Verify the file path exists and is accessible
- **"Permission denied"**: Check file permissions and write access to receive directory
- **"Transfer incomplete"**: Network interruption occurred, retry the transfer

### Firewall Configuration
If connecting over the internet, ensure:
- Server port is open in firewall
- Router port forwarding is configured (if needed)
- Network allows the specified traffic

## Development

### Running Tests
```bash
# Create test files
echo "Test content" > examples/test1.txt
echo "More test content" > examples/test2.txt

# Start server in one terminal
python src/server/file_server.py

# Send test files in another terminal
python src/client/file_client.py examples/test1.txt examples/test2.txt
```

### Extending the Protocol
The protocol can be extended by:
1. Adding new message types to `src/common/protocol.py`
2. Implementing handlers in server and client
3. Updating documentation

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues, feature requests, and pull requests to improve the project.