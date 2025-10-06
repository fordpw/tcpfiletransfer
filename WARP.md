# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a TCP-based file transfer system with a custom binary protocol. The architecture consists of:

- **Server** (`src/server/file_server.py`): Multi-threaded TCP server that receives files
- **Client** (`src/client/file_client.py`): TCP client that sends files to servers  
- **Protocol** (`src/common/protocol.py`): Shared binary protocol implementation

The system uses a custom message-based protocol with acknowledgments, chunked transfers, and progress tracking.

## Development Commands

### Running the Server
```bash
# Start server on localhost:8888
python src/server/file_server.py

# Start server on custom host/port
python src/server/file_server.py --host 0.0.0.0 --port 9999

# Custom receive directory
python src/server/file_server.py --receive-dir /path/to/save/files

# Using example script
python examples/start_server.py
```

### Sending Files (Client)
```bash
# Send single file
python src/client/file_client.py file.txt

# Send multiple files
python src/client/file_client.py file1.txt file2.pdf file3.jpg

# Connect to remote server
python src/client/file_client.py --host 192.168.1.100 --port 9999 file.txt

# Using example script
python examples/send_file.py
```

### Testing the System
```bash
# Terminal 1: Start server
python src/server/file_server.py

# Terminal 2: Send test files
python src/client/file_client.py examples/sample.txt

# Create test files for development
echo "Test content" > test1.txt
echo "More test content" > test2.txt
python src/client/file_client.py test1.txt test2.txt
```

## Architecture Details

### Protocol Design
The system uses a binary message protocol with 8-byte headers:
- **Header Format**: `[4 bytes: Message Type][4 bytes: Data Length][Variable: Data]`
- **Message Types**: `FINFO`, `FDATA`, `FEND`, `ACK`, `ERR`
- **Transfer Flow**: File info → Data chunks → End marker (with ACK responses)

### Key Components

#### Protocol Layer (`src/common/protocol.py`)
- **Message packing/unpacking**: Binary protocol handling with struct format `!I`
- **File info messages**: JSON-encoded filename and size metadata
- **Security features**: Filename sanitization, path traversal prevention
- **Chunk size**: 4KB chunks for file data transfer

#### Server Architecture (`src/server/file_server.py`)
- **Threading model**: One thread per client connection using `threading.Thread`
- **File handling**: Automatic duplicate filename resolution with numbered suffixes
- **Error recovery**: Incomplete transfers are automatically cleaned up
- **Safety**: Files saved with sanitized names in configured receive directory

#### Client Architecture (`src/client/file_client.py`)
- **Single connection per file**: New socket connection for each file transfer
- **Progress reporting**: Real-time progress updates during transfer
- **Error handling**: Proper cleanup on connection or protocol errors
- **Multiple file support**: Sequential file transfers

### Import Path Management
Both client and server add the parent directory to `sys.path` to import common modules:
```python
sys.path.append(str(Path(__file__).parent.parent))
```

### File Structure Patterns
- **Server files**: Saved to configurable `receive_dir` (default: `received_files/`)
- **Filename conflicts**: Handled with `_1`, `_2`, etc. suffixes
- **Path security**: Only basename used, full paths stripped for security

## Development Patterns

### Adding New Message Types
1. Define message constant in `protocol.py` (4-byte identifier)
2. Add packing/unpacking functions if needed
3. Update server and client handlers
4. Test with new protocol flow

### Error Handling Approach
- **Protocol errors**: Custom `ProtocolError` exception with descriptive messages
- **Network errors**: Proper socket cleanup in `finally` blocks
- **File errors**: Graceful handling with cleanup of partial transfers

### Threading Considerations
- Server uses daemon threads for client connections
- Each client gets isolated thread context
- Server shutdown via KeyboardInterrupt (Ctrl+C)

### Security Model
- Filename sanitization removes path separators and dangerous characters
- File size limits enforced at protocol level
- No authentication (intended for trusted networks)

## Testing Guidelines

### Manual Testing Flow
1. Start server in one terminal
2. Create test files of various sizes (text, binary)
3. Test single and multiple file transfers
4. Verify files received correctly in `received_files/`
5. Test error conditions (file not found, server down, etc.)

### Network Testing
- Test localhost connections first
- Use `--host 0.0.0.0` for network access
- Test with firewall/network restrictions
- Verify large file transfers complete successfully

### Binary File Testing
Use `examples/binary_sample.py` or create binary test files:
```bash
# Create binary test file
python -c "with open('test.bin', 'wb') as f: f.write(b'\\x00\\x01\\x02' * 1000)"
python src/client/file_client.py test.bin
```

## Dependencies and Requirements
- **Python**: 3.6+ (uses type hints and pathlib)
- **Standard library only**: No external dependencies required
- **Cross-platform**: Works on Windows, macOS, and Linux