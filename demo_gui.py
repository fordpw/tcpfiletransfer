#!/usr/bin/env python3
"""
TCP File Transfer GUI Demo

Demo script showing GUI functionality and providing basic testing.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_tkinter():
    """Check if tkinter is available."""
    try:
        import tkinter
        print("✅ Tkinter available")
        return True
    except ImportError:
        print("❌ Tkinter not available")
        print("   Install tkinter: sudo apt-get install python3-tk (Ubuntu/Debian)")
        return False

def check_modules():
    """Check if all required modules can be imported."""
    modules_to_check = [
        ("common.protocol", "Protocol definitions"),
        ("client.file_client", "File client"),
        ("server.file_server", "File server"),
        ("gui.drag_drop", "Drag-and-drop support"),
        ("gui.server_integration", "Server integration"),
        ("gui.file_transfer_gui", "Main GUI")
    ]
    
    all_good = True
    
    for module_name, description in modules_to_check:
        try:
            __import__(module_name)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            all_good = False
    
    return all_good

def check_optional_features():
    """Check optional features."""
    try:
        import tkinterdnd2
        print("✅ Enhanced drag-and-drop (tkinterdnd2) available")
        return True
    except ImportError:
        print("⚠️  Enhanced drag-and-drop not available")
        print("   Install with: pip install tkinterdnd2")
        print("   (GUI will work with click-to-browse fallback)")
        return False

def create_sample_files():
    """Create sample files for testing."""
    samples_dir = Path("sample_files")
    samples_dir.mkdir(exist_ok=True)
    
    sample_files = [
        ("hello.txt", "Hello, World!\nThis is a test file for the TCP File Transfer GUI."),
        ("data.txt", "Sample data file with some content.\n" + "Line " * 10 + "\n" + "123" * 100),
        ("small.bin", b"\\x00\\x01\\x02\\x03\\xFF\\xFE\\xFD\\xFC" * 64)  # Binary file
    ]
    
    created_files = []
    
    for filename, content in sample_files:
        file_path = samples_dir / filename
        try:
            if isinstance(content, str):
                file_path.write_text(content)
            else:
                file_path.write_bytes(content)
            created_files.append(str(file_path))
            print(f"✅ Created sample file: {file_path}")
        except Exception as e:
            print(f"❌ Failed to create {file_path}: {e}")
    
    return created_files

def print_usage_instructions():
    """Print usage instructions."""
    print("\\n" + "="*60)
    print("🚀 TCP FILE TRANSFER GUI - READY TO USE")
    print("="*60)
    print()
    print("📁 LAUNCH OPTIONS:")
    print("   Windows:  Double-click 'launch_gui.bat'")
    print("   Command:  python launch_gui.py")
    print()
    print("🎯 QUICK TEST PROCEDURE:")
    print("   1. Launch the GUI")
    print("   2. Go to 'Receive Files (Server)' tab")
    print("   3. Click 'Start Server'")
    print("   4. Go to 'Send Files (Client)' tab") 
    print("   5. Drag sample files or click 'Browse Files'")
    print("   6. Click 'Send Files'")
    print()
    print("📂 Sample files created in 'sample_files/' directory:")
    sample_files = list(Path("sample_files").glob("*")) if Path("sample_files").exists() else []
    for f in sample_files:
        size = f.stat().st_size
        print(f"   - {f.name} ({size} bytes)")
    print()
    print("🔧 TROUBLESHOOTING:")
    print("   - See GUI_README.md for detailed instructions")
    print("   - Check firewall if connection issues occur") 
    print("   - Use localhost (127.0.0.1) for local testing")
    print()

def main():
    """Main demo function."""
    print("TCP File Transfer GUI - System Check & Demo")
    print("="*50)
    print()
    
    # System checks
    if not check_python_version():
        return False
    
    if not check_tkinter():
        return False
    
    if not check_modules():
        print("\\n❌ Some required modules failed to import.")
        print("Make sure you're running from the project root directory.")
        return False
    
    print("\\n🔍 OPTIONAL FEATURES:")
    check_optional_features()
    
    print("\\n📝 CREATING SAMPLE FILES:")
    create_sample_files()
    
    print_usage_instructions()
    
    # Ask if user wants to launch GUI
    try:
        response = input("🚀 Launch GUI now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("Starting GUI...")
            from gui.file_transfer_gui import main as gui_main
            gui_main()
    except KeyboardInterrupt:
        print("\\nDemo cancelled.")
    except Exception as e:
        print(f"Error launching GUI: {e}")
    
    return True

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\\nDemo interrupted.")
    except Exception as e:
        print(f"Demo error: {e}")
        input("Press Enter to exit...")