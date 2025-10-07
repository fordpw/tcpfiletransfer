#!/usr/bin/env python3
"""
TCP File Transfer GUI Application

A user-friendly graphical interface for the TCP file transfer system
with drag-and-drop functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import queue
import socket
from pathlib import Path
from typing import List, Optional

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from client.file_client import FileTransferClient
from common.protocol import ProtocolError
from gui.server_integration import handle_client_connection
from gui.drag_drop import DragDropFrame, create_root_with_dnd


class FileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP File Transfer - Drag & Drop Interface")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Application state
        self.server = None
        self.server_thread = None
        self.server_running = False
        self.files_to_send = []
        
        # Queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Create GUI components
        self.create_widgets()
        self.setup_drag_drop()
        
        # Start message processing
        self.process_messages()
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_client_tab()
        self.create_server_tab()
        
    def create_client_tab(self):
        """Create the client (file sending) tab."""
        client_frame = ttk.Frame(self.notebook)
        self.notebook.add(client_frame, text="Send Files (Client)")
        
        # Connection settings frame
        conn_frame = ttk.LabelFrame(client_frame, text="Server Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Host and port inputs
        settings_frame = ttk.Frame(conn_frame)
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_var = tk.StringVar(value="localhost")
        self.host_entry = ttk.Entry(settings_frame, textvariable=self.host_var, width=20)
        self.host_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(settings_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar(value="8888")
        self.port_entry = ttk.Entry(settings_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=3, padx=(0, 10))
        
        # File selection frame
        file_frame = ttk.LabelFrame(client_frame, text="Files to Send", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Drag and drop area
        self.drop_frame_wrapper = DragDropFrame(
            file_frame,
            on_drop_callback=self._on_files_dropped,
            bg='#f0f0f0',
            relief=tk.SUNKEN,
            bd=2
        )
        self.drop_frame_wrapper.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Use the actual frame from the wrapper
        self.drop_frame = self.drop_frame_wrapper.frame
        
        self.drop_label = tk.Label(
            self.drop_frame,
            text="Drag & Drop Files Here\n\nOr click 'Browse Files' button below",
            bg='#f0f0f0',
            fg='#666666',
            font=('Arial', 12),
            justify=tk.CENTER
        )
        self.drop_label.pack(expand=True)
        
        # File list
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Browse Files", command=self.browse_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear List", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected_files).pack(side=tk.LEFT, padx=5)
        
        # Send button
        self.send_button = ttk.Button(button_frame, text="Send Files", command=self.send_files, state=tk.DISABLED)
        self.send_button.pack(side=tk.RIGHT)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(client_frame, text="Transfer Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready to send files...")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
    def create_server_tab(self):
        """Create the server (file receiving) tab."""
        server_frame = ttk.Frame(self.notebook)
        self.notebook.add(server_frame, text="Receive Files (Server)")
        
        # Server settings frame
        settings_frame = ttk.LabelFrame(server_frame, text="Server Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Server configuration
        config_frame = ttk.Frame(settings_frame)
        config_frame.pack(fill=tk.X)
        
        ttk.Label(config_frame, text="Listen Host:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.server_host_var = tk.StringVar(value="localhost")
        self.server_host_entry = ttk.Entry(config_frame, textvariable=self.server_host_var, width=20)
        self.server_host_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.server_port_var = tk.StringVar(value="8888")
        self.server_port_entry = ttk.Entry(config_frame, textvariable=self.server_port_var, width=10)
        self.server_port_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Receive directory
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(dir_frame, text="Save Directory:").pack(anchor=tk.W)
        self.save_dir_var = tk.StringVar(value=str(Path.cwd() / "received_files"))
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.save_dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.save_dir_var)
        self.save_dir_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        ttk.Button(dir_entry_frame, text="Browse", command=self.browse_save_directory).pack(side=tk.RIGHT)
        
        # Server control buttons
        control_frame = ttk.Frame(settings_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_server_button = ttk.Button(control_frame, text="Start Server", command=self.start_server)
        self.start_server_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_server_button = ttk.Button(control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_server_button.pack(side=tk.LEFT)
        
        # Server status
        self.server_status_var = tk.StringVar(value="Server stopped")
        ttk.Label(control_frame, textvariable=self.server_status_var, foreground="red").pack(side=tk.RIGHT)
        
        # Server log frame
        log_frame = ttk.LabelFrame(server_frame, text="Server Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.server_log = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.server_log.pack(fill=tk.BOTH, expand=True)
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_server_log).pack(anchor=tk.E, pady=(5, 0))
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        # Enhanced drag and drop is handled by DragDropFrame
        # Add click handler to label as fallback
        self.drop_label.bind("<Button-1>", self.on_drop_click)
    
    def on_drop_click(self, event):
        """Handle click on drop area (opens file dialog)."""
        self.browse_files()
    
    def _on_files_dropped(self, files):
        """Handle files dropped onto the drop area."""
        for file_path in files:
            if file_path not in self.files_to_send:
                self.files_to_send.append(file_path)
        self.update_file_list()
    
    def browse_files(self):
        """Open file browser to select files."""
        files = filedialog.askopenfilenames(
            title="Select files to send",
            filetypes=[("All files", "*.*")]
        )
        if files:
            for file_path in files:
                if file_path not in self.files_to_send:
                    self.files_to_send.append(file_path)
            self.update_file_list()
    
    def browse_save_directory(self):
        """Browse for directory to save received files."""
        directory = filedialog.askdirectory(
            title="Select directory to save received files",
            initialdir=self.save_dir_var.get()
        )
        if directory:
            self.save_dir_var.set(directory)
    
    def update_file_list(self):
        """Update the file listbox."""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.files_to_send:
            filename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            size_str = self.format_file_size(size)
            self.file_listbox.insert(tk.END, f"{filename} ({size_str})")
        
        # Enable/disable send button
        self.send_button.config(state=tk.NORMAL if self.files_to_send else tk.DISABLED)
        
        # Update drop label
        if self.files_to_send:
            count = len(self.files_to_send)
            self.drop_label.config(
                text=f"{count} file{'s' if count != 1 else ''} selected\n\nDrag more files here or use buttons below",
                fg='#333333'
            )
        else:
            self.drop_label.config(
                text="Drag & Drop Files Here\n\nOr click 'Browse Files' button below",
                fg='#666666'
            )
    
    def format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def clear_files(self):
        """Clear all files from the list."""
        self.files_to_send.clear()
        self.update_file_list()
    
    def remove_selected_files(self):
        """Remove selected files from the list."""
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):  # Remove in reverse order
            del self.files_to_send[index]
        self.update_file_list()
    
    def send_files(self):
        """Send all files in the list."""
        if not self.files_to_send:
            return
        
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
            return
        
        if not host:
            messagebox.showerror("Error", "Please enter a host address")
            return
        
        # Disable send button and start progress
        self.send_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.progress_var.set("Sending files...")
        
        # Send files in a separate thread
        thread = threading.Thread(
            target=self._send_files_thread,
            args=(host, port, self.files_to_send.copy())
        )
        thread.daemon = True
        thread.start()
    
    def _send_files_thread(self, host, port, file_paths):
        """Thread function to send files."""
        try:
            client = FileTransferClient(host, port)
            
            for i, file_path in enumerate(file_paths, 1):
                self.message_queue.put(('progress', f"Sending file {i}/{len(file_paths)}: {os.path.basename(file_path)}"))
                
                try:
                    client.send_file(file_path)
                    self.message_queue.put(('log', f"✓ Successfully sent: {os.path.basename(file_path)}"))
                except Exception as e:
                    self.message_queue.put(('error', f"✗ Failed to send {os.path.basename(file_path)}: {str(e)}"))
            
            self.message_queue.put(('complete', f"Transfer complete! Sent {len(file_paths)} files."))
            
        except Exception as e:
            self.message_queue.put(('error', f"Connection failed: {str(e)}"))
    
    def start_server(self):
        """Start the file transfer server."""
        try:
            host = self.server_host_var.get().strip()
            port = int(self.server_port_var.get())
            save_dir = Path(self.save_dir_var.get())
            
            # Create save directory if it doesn't exist
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(
                target=self._run_server_thread,
                args=(host, port, save_dir)
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Update UI
            self.server_running = True
            self.start_server_button.config(state=tk.DISABLED)
            self.stop_server_button.config(state=tk.NORMAL)
            self.server_status_var.set(f"Server running on {host}:{port}")
            self.server_log.config(foreground="green")
            
            self.log_server_message(f"Server started on {host}:{port}")
            self.log_server_message(f"Files will be saved to: {save_dir}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop the file transfer server."""
        self.server_running = False
        
        # Update UI
        self.start_server_button.config(state=tk.NORMAL)
        self.stop_server_button.config(state=tk.DISABLED)
        self.server_status_var.set("Server stopped")
        self.server_log.config(foreground="red")
        
        self.log_server_message("Server stopped by user")
    
    def _run_server_thread(self, host, port, save_dir):
        """Thread function to run the server."""
        try:
            # Create a simple server socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(5)
            server_socket.settimeout(1.0)  # Allow periodic checking of server_running
            
            self.message_queue.put(('server_log', f"Server listening on {host}:{port}"))
            
            while self.server_running:
                try:
                    client_socket, address = server_socket.accept()
                    self.message_queue.put(('server_log', f"New connection from {address}"))
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address, save_dir)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue  # Check if server should still be running
                except Exception as e:
                    if self.server_running:
                        self.message_queue.put(('server_error', f"Server error: {str(e)}"))
            
        except Exception as e:
            self.message_queue.put(('server_error', f"Failed to start server: {str(e)}"))
        finally:
            try:
                server_socket.close()
            except:
                pass
    
    def _handle_client(self, client_socket, address, save_dir):
        """Handle a client connection."""
        try:
            handle_client_connection(client_socket, address, save_dir, self._server_callback)
        except Exception as e:
            self.message_queue.put(('server_error', f"Error handling client {address}: {str(e)}"))
    
    def _server_callback(self, message):
        """Callback for server messages."""
        self.message_queue.put(('server_log', message))
    
    def log_server_message(self, message):
        """Add a message to the server log."""
        self.server_log.config(state=tk.NORMAL)
        self.server_log.insert(tk.END, f"{message}\n")
        self.server_log.see(tk.END)
        self.server_log.config(state=tk.DISABLED)
    
    def clear_server_log(self):
        """Clear the server log."""
        self.server_log.config(state=tk.NORMAL)
        self.server_log.delete(1.0, tk.END)
        self.server_log.config(state=tk.DISABLED)
    
    def process_messages(self):
        """Process messages from background threads."""
        try:
            while True:
                message_type, message = self.message_queue.get_nowait()
                
                if message_type == 'progress':
                    self.progress_var.set(message)
                elif message_type == 'log':
                    print(message)  # For now, just print to console
                elif message_type == 'error':
                    print(f"Error: {message}")
                    messagebox.showerror("Transfer Error", message)
                elif message_type == 'complete':
                    self.progress_var.set(message)
                    self.progress_bar.stop()
                    self.send_button.config(state=tk.NORMAL)
                    messagebox.showinfo("Success", message)
                elif message_type == 'server_log':
                    self.log_server_message(message)
                elif message_type == 'server_error':
                    self.log_server_message(f"ERROR: {message}")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)


def main():
    """Main function to run the GUI application."""
    root = create_root_with_dnd()
    app = FileTransferGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        if hasattr(app, 'server_running'):
            app.server_running = False


if __name__ == '__main__':
    main()