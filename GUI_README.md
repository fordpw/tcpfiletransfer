# TCP File Transfer - Graphical User Interface

A modern, user-friendly drag-and-drop interface for the TCP File Transfer system.

## Features

### 🎯 **Dual Mode Interface**
- **Client Mode**: Send files with drag-and-drop functionality
- **Server Mode**: Receive files with real-time logging

### 🖱️ **Drag & Drop Support**
- Drag files directly from your file manager
- Visual feedback during drag operations
- Automatic fallback to click-to-browse if advanced libraries aren't available

### 📊 **Progress Tracking**
- Real-time progress bars for file transfers
- Detailed status messages
- Transfer completion notifications

### 🔧 **Easy Configuration**
- Simple host/port configuration
- Customizable save directory for received files
- One-click server start/stop

### 🪟 **Cross-Platform**
- Works on Windows, macOS, and Linux
- Uses only built-in Python libraries (tkinter)
- Optional enhanced drag-drop with tkinterdnd2

## Quick Start

### Prerequisites
- Python 3.6 or higher
- No additional dependencies required (uses built-in tkinter)

### Launch the GUI

#### Windows
Double-click `launch_gui.bat` or run:
```batch
python launch_gui.py
```

#### macOS/Linux
```bash
python3 launch_gui.py
```

## Usage Guide

### 📤 Sending Files (Client Mode)

1. **Switch to "Send Files (Client)" tab**
2. **Configure connection**:
   - Host: Enter the server IP address (default: localhost)
   - Port: Enter the server port (default: 8888)

3. **Add files** (multiple ways):
   - **Drag & Drop**: Drag files from your file manager into the drop area
   - **Browse Button**: Click "Browse Files" to select files
   - **Click Drop Area**: Click the gray drop area to open file browser

4. **Manage file list**:
   - View selected files with sizes
   - Remove individual files (select and click "Remove Selected")
   - Clear entire list ("Clear List" button)

5. **Send files**: Click "Send Files" button
   - Progress bar shows transfer status
   - Success/error messages appear automatically

### 📥 Receiving Files (Server Mode)

1. **Switch to "Receive Files (Server)" tab**
2. **Configure server**:
   - Listen Host: Usually "localhost" or "0.0.0.0" for all interfaces
   - Port: Server port (default: 8888)
   - Save Directory: Choose where to save received files

3. **Start server**: Click "Start Server"
   - Server status shows "Server running on [host]:[port]"
   - Real-time log shows all server activity

4. **Monitor transfers**:
   - See incoming connections in real-time
   - Track file reception progress
   - View success/error messages

5. **Stop server**: Click "Stop Server" when done

## File Management

### Automatic File Handling
- **Duplicate names**: Files with existing names get numbered suffixes (file_1.txt, file_2.txt, etc.)
- **Path security**: Filenames are automatically sanitized for security
- **Incomplete transfers**: Failed transfers are automatically cleaned up

### Supported File Types
- All file types are supported
- Binary and text files
- Large files are transferred in chunks for reliability

## Advanced Features

### Enhanced Drag & Drop
For the best experience, you can install `tkinterdnd2`:
```bash
pip install tkinterdnd2
```

This enables:
- True external drag-and-drop from file managers
- Visual drag feedback
- Multi-file drag support

Without tkinterdnd2, the GUI falls back to click-to-browse functionality.

### Network Configuration

#### Local Network Transfer
- Server Host: `0.0.0.0` (listens on all network interfaces)
- Client Host: Server computer's IP address
- Ensure firewall allows the chosen port

#### Internet Transfer
- Server needs port forwarding configured on router
- Use external IP address for remote connections
- Consider security implications of internet-exposed servers

## Troubleshooting

### Common Issues

#### "Python not found"
- Install Python 3.6+ from python.org
- Make sure "Add Python to PATH" was selected during installation
- Try `python3` instead of `python`

#### "Connection refused"
- Make sure server is running first
- Check host and port settings match between client and server
- Verify firewall isn't blocking the connection

#### "Drag and drop not working"
- The GUI automatically falls back to click-to-browse
- For full drag-drop, install: `pip install tkinterdnd2`
- Click the drop area to browse for files

#### "Files not appearing in save directory"
- Check the save directory path is correct
- Verify you have write permissions to the directory
- Look for error messages in the server log

### GUI-Specific Issues

#### "Interface looks cramped"
- The window is resizable - drag corners to make it larger
- Minimum size is 600x400 pixels

#### "Can't see server log messages"
- Use the "Clear Log" button if the log gets too long
- Scroll within the log area to see older messages

## File Structure

The GUI is organized as follows:
```
tcpfiletransfer/
├── src/
│   ├── gui/
│   │   ├── file_transfer_gui.py     # Main GUI application
│   │   ├── server_integration.py   # Server integration module
│   │   └── drag_drop.py            # Enhanced drag-drop support
│   ├── client/
│   │   └── file_client.py          # TCP client (used by GUI)
│   ├── server/
│   │   └── file_server.py          # TCP server (reference)
│   └── common/
│       └── protocol.py             # Protocol definitions
├── launch_gui.py                   # GUI launcher script
├── launch_gui.bat                  # Windows launcher
└── GUI_README.md                   # This file
```

## Technical Details

### Architecture
- **Threading**: File transfers and server operations run in background threads
- **Thread Safety**: GUI updates are handled through thread-safe message queues
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Protocol**: Uses the same robust TCP protocol as the command-line tools

### Performance
- **Chunk-based Transfer**: Large files are sent in 4KB chunks
- **Progress Updates**: Real-time progress tracking for all operations
- **Memory Efficient**: Streams file data without loading entire files into memory

### Security
- **Filename Sanitization**: Prevents directory traversal attacks
- **Path Validation**: Only basenames are used for security
- **Error Isolation**: Network errors don't crash the GUI

## License

This GUI is part of the TCP File Transfer project and is provided as-is for educational and development purposes.

## Contributing

Found a bug or want to add a feature? The GUI is designed to be easily extensible:

- `file_transfer_gui.py`: Main GUI logic
- `drag_drop.py`: Drag-and-drop functionality
- `server_integration.py`: Server integration layer

Feel free to submit issues and pull requests!