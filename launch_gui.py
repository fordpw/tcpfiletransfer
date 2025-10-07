#!/usr/bin/env python3
"""
TCP File Transfer GUI Launcher

Simple launcher script for the TCP file transfer GUI application.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from gui.file_transfer_gui import main
    
    if __name__ == '__main__':
        print("Starting TCP File Transfer GUI...")
        print("Make sure Python 3.6+ is installed.")
        print("The application uses only built-in Python libraries.\n")
        
        # Change to the project directory
        os.chdir(Path(__file__).parent)
        
        # Run the GUI
        main()
        
except ImportError as e:
    print(f"Error importing GUI modules: {e}")
    print("\nMake sure you're running this from the project root directory.")
    print("Required directory structure:")
    print("  tcpfiletransfer/")
    print("  ├── src/")
    print("  │   ├── gui/")
    print("  │   │   ├── file_transfer_gui.py")
    print("  │   │   └── server_integration.py")
    print("  │   ├── client/")
    print("  │   │   └── file_client.py")
    print("  │   ├── server/")
    print("  │   │   └── file_server.py")
    print("  │   └── common/")
    print("  │       └── protocol.py")
    print("  └── launch_gui.py")
    sys.exit(1)
    
except Exception as e:
    print(f"Error starting GUI: {e}")
    input("Press Enter to exit...")
    sys.exit(1)