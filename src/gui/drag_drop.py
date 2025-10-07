#!/usr/bin/env python3
"""
Enhanced drag and drop functionality

Provides drag and drop support for the file transfer GUI.
Falls back to basic click-to-browse if advanced libraries aren't available.
"""

import tkinter as tk
import os
import sys
from pathlib import Path

# Try to import tkinterdnd2 for full drag and drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    ADVANCED_DND_AVAILABLE = True
    print("Advanced drag-and-drop support available")
except ImportError:
    ADVANCED_DND_AVAILABLE = False
    TkinterDnD = tk
    DND_FILES = None
    print("Using basic drag-and-drop (click to browse)")


class DragDropFrame:
    """Frame with drag and drop capabilities."""
    
    def __init__(self, parent, on_drop_callback, **kwargs):
        self.on_drop_callback = on_drop_callback
        
        # Create frame
        self.frame = tk.Frame(parent, **kwargs)
        
        # Setup drag and drop
        if ADVANCED_DND_AVAILABLE:
            self._setup_advanced_dnd()
        else:
            self._setup_basic_dnd()
    
    def _setup_advanced_dnd(self):
        """Setup advanced drag and drop using tkinterdnd2."""
        self.frame.drop_target_register(DND_FILES)
        self.frame.dnd_bind('<<Drop>>', self._on_drop_advanced)
        self.frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
    
    def _setup_basic_dnd(self):
        """Setup basic drag and drop (click to browse)."""
        self.frame.bind("<Button-1>", self._on_click_browse)
        self.frame.bind("<Enter>", self._on_mouse_enter)
        self.frame.bind("<Leave>", self._on_mouse_leave)
    
    def _on_drop_advanced(self, event):
        """Handle advanced drag and drop."""
        files = []
        
        # Parse the dropped data
        if event.data:
            # Split the data by spaces, but handle quoted filenames
            import shlex
            try:
                file_paths = shlex.split(event.data)
            except ValueError:
                # Fallback for malformed data
                file_paths = event.data.split()
            
            # Filter to only existing files
            for file_path in file_paths:
                file_path = file_path.strip()
                if file_path and os.path.isfile(file_path):
                    files.append(file_path)
        
        if files:
            self.on_drop_callback(files)
        
        # Reset frame appearance
        original_bg = getattr(self, '_original_bg', '#f0f0f0')
        self.frame.config(bg=original_bg, relief=tk.SUNKEN)
    
    def _on_drag_enter(self, event):
        """Handle drag enter event."""
        if not hasattr(self, '_original_bg'):
            self._original_bg = self.frame.cget('bg')
        self.frame.config(bg='#e6f3ff', relief=tk.RAISED)
    
    def _on_drag_leave(self, event):
        """Handle drag leave event."""
        original_bg = getattr(self, '_original_bg', '#f0f0f0')
        self.frame.config(bg=original_bg, relief=tk.SUNKEN)
    
    def _on_click_browse(self, event):
        """Handle click to browse for files."""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="Select files to send",
            filetypes=[("All files", "*.*")]
        )
        if files:
            self.on_drop_callback(list(files))
    
    def _on_mouse_enter(self, event):
        """Handle mouse enter for basic mode."""
        if not ADVANCED_DND_AVAILABLE:
            self.frame.config(cursor="hand2")
    
    def _on_mouse_leave(self, event):
        """Handle mouse leave for basic mode."""
        if not ADVANCED_DND_AVAILABLE:
            self.frame.config(cursor="")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame."""
        self.frame.grid(**kwargs)
    
    def config(self, **kwargs):
        """Configure the frame."""
        self.frame.config(**kwargs)
    
    def winfo_children(self):
        """Get frame children."""
        return self.frame.winfo_children()


def create_root_with_dnd():
    """Create a root window with drag and drop support."""
    if ADVANCED_DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    return root


def test_drag_drop():
    """Test the drag and drop functionality."""
    def on_files_dropped(files):
        print(f"Files dropped: {files}")
        for file_path in files:
            print(f"  - {file_path} ({os.path.getsize(file_path)} bytes)")
    
    root = create_root_with_dnd()
    root.title("Drag and Drop Test")
    root.geometry("400x300")
    
    # Create drag drop area
    dnd_frame = DragDropFrame(
        root,
        on_drop_callback=on_files_dropped,
        bg='#f0f0f0',
        relief=tk.SUNKEN,
        bd=2
    )
    dnd_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Add label
    if ADVANCED_DND_AVAILABLE:
        label_text = "Drag and drop files here from your file manager"
    else:
        label_text = "Click here to browse for files\n(Advanced drag-and-drop not available)"
    
    label = tk.Label(
        dnd_frame.frame,
        text=label_text,
        bg='#f0f0f0',
        fg='#666666',
        font=('Arial', 12),
        justify=tk.CENTER
    )
    label.pack(expand=True)
    
    root.mainloop()


if __name__ == '__main__':
    test_drag_drop()