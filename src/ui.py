import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
from src.file_io import select_folder, select_save_location, save_to_excel
from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
import sys
import os
import threading

class ProgressDialog:
    def __init__(self, parent, title="Progress", mode="indeterminate"):
        self.parent = parent
        self.cancelled = False
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.eval('tk::PlaceWindow . center')
        
        # Status label
        self.status_label = tk.Label(self.dialog, text="Starting...", wraplength=480)
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        if mode == "determinate":
            self.progress_bar = ttk.Progressbar(
                self.dialog, 
                variable=self.progress_var, 
                maximum=100, 
                mode="determinate"
            )
        else:
            self.progress_bar = ttk.Progressbar(
                self.dialog, 
                mode="indeterminate"
            )
            self.progress_bar.start(10)  # Start the animation
        
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        
        # Cancel button
        self.cancel_button = tk.Button(
            self.dialog, 
            text="Cancel", 
            command=self.cancel_operation
        )
        self.cancel_button.pack(pady=10)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_operation)
    
    def update_status(self, message):
        """Update the status message"""
        if not self.cancelled:
            self.status_label.config(text=message)
            self.dialog.update_idletasks()
    
    def update_progress(self, value):
        """Update progress bar (for determinate mode)"""
        if not self.cancelled:
            self.progress_var.set(value)
            self.dialog.update_idletasks()
    
    def cancel_operation(self):
        """Cancel the operation"""
        self.cancelled = True
        self.cancel_button.config(state="disabled", text="Cancelling...")
        self.update_status("Cancelling operation...")
    
    def is_cancelled(self):
        """Check if operation was cancelled"""
        return self.cancelled
    
    def close(self):
        """Close the dialog"""
        if hasattr(self.progress_bar, 'stop'):
            self.progress_bar.stop()
        self.dialog.destroy()

def ask_user_choice():
    root = tk.Tk()
    root.title("Folder and File Scanner")
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller's temp path
    else:
        base_path = os.path.abspath(".")

    icon_path = os.path.join(base_path, "icon", "folderScanner.ico")
    root.iconbitmap(icon_path)
    root.geometry("600x400")
    root.eval('tk::PlaceWindow . center')

    # ---------- Main Instructions ----------
    guide_text = (
        "Welcome to Folder and File Scanner!\n"
        "It simply allows scanning, reporting and replicating folder contents.\n\n"
        "• Check 'Include Files' to include files in the scan.\n"
        "• Use the Filter text to filter by specific file types.\n"
        "• Check 'Replicate Structure' to copy the folder (and files) layout elsewhere.\n"
        "• Click 'Scan' to start the activity.\n\n"

    )
    tk.Label(root, text=guide_text, justify="left", wraplength=580, fg="blue").pack(pady=10)

    # ---------- Options Frame ----------
    options_frame = tk.Frame(root)
    options_frame.pack(fill="x", padx=20)

    include_files_var = tk.BooleanVar()
    replicate_var = tk.BooleanVar()
    extensions_var = tk.StringVar()

    def toggle_extensions_input(*args):
        if include_files_var.get():
            extensions_frame.pack(fill="x", padx=20, pady=5)
        else:
            extensions_frame.forget()

    include_files_var.trace_add("write", toggle_extensions_input)

    # Include files checkbox
    tk.Checkbutton(options_frame, text="Include Files", variable=include_files_var, anchor="w").pack(anchor="w", pady=2)
    # Replicate checkbox
    tk.Checkbutton(options_frame, text="Replicate Structure", variable=replicate_var, anchor="w").pack(anchor="w", pady=2)
    
    # ---------- Extensions Entry (initially hidden) ----------
    extensions_frame = tk.Frame(root)
    tk.Label(extensions_frame, text="Provide file extensions, seperated by ',' (example: .pdf, .docx)").pack(anchor="w")
    tk.Entry(extensions_frame, textvariable=extensions_var, width=50).pack(anchor="w", pady=2)

    # ---------- Scan Button ----------
    tk.Button(root, text="Scan", command=lambda: start_scan(), width=20, height=2).pack(pady=20)

    # ---------- Logic for Scanning ----------
    def start_scan():
        try:
            source_folder = select_folder("Select Folder to Scan")
            save_location = select_save_location()

            include_files = include_files_var.get()
            extensions = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()] if include_files else None
        
            if replicate_var.get():
                dest_folder = select_folder("Select Destination for Replication")
                # Use threaded scanning and replication with progress
                run_replication_with_progress(source_folder, dest_folder, save_location, include_files, extensions)
            else:
                # Use threaded scanning with progress
                run_scanning_with_progress(source_folder, save_location, include_files, extensions)

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    def run_scanning_with_progress(source_folder, save_location, include_files, extensions):
        """Run scanning operation with progress dialog"""
        progress_dialog = ProgressDialog(root, "Scanning Progress", "indeterminate")
        result = {"data": None, "error": None, "cancelled": False}
        
        def scanning_worker():
            try:
                progress_callbacks = {
                    'update_status': progress_dialog.update_status,
                    'check_cancelled': progress_dialog.is_cancelled
                }
                
                data = collect_folders_and_files(source_folder, include_files, extensions, progress_callbacks)
                
                if not progress_dialog.is_cancelled():
                    progress_dialog.update_status("Saving to Excel...")
                    save_to_excel(data, save_location)
                    result["data"] = data
                else:
                    result["cancelled"] = True
                    
            except Exception as e:
                result["error"] = str(e)
        
        # Start the scanning in a separate thread
        thread = threading.Thread(target=scanning_worker)
        thread.daemon = True
        thread.start()
        
        # Wait for completion or cancellation
        def check_completion():
            if thread.is_alive():
                root.after(100, check_completion)  # Check again in 100ms
            else:
                progress_dialog.close()
                
                if result["cancelled"]:
                    messagebox.showinfo("Cancelled", "Scanning operation was cancelled.")
                elif result["error"]:
                    messagebox.showerror("Error", f"An error occurred:\n{result['error']}")
                else:
                    message = f"Scan completed successfully.\nReport has been saved to:\n{save_location}"
                    messagebox.showinfo("Completed", message)
                    
                root.destroy()
        
        root.after(100, check_completion)

    def run_replication_with_progress(source_folder, dest_folder, save_location, include_files, extensions):
        """Run replication operation with progress dialog"""
        progress_dialog = ProgressDialog(root, "Replication Progress", "determinate")
        result = {"data": None, "error": None, "cancelled": False}
        
        def replication_worker():
            try:
                progress_callbacks = {
                    'update_status': progress_dialog.update_status,
                    'update_progress': progress_dialog.update_progress,
                    'check_cancelled': progress_dialog.is_cancelled
                }
                
                replication_results = replicate_folder_structure(
                    source_folder, dest_folder, include_files, extensions, progress_callbacks
                )
                
                if not progress_dialog.is_cancelled():
                    progress_dialog.update_status("Saving to Excel...")
                    pd.DataFrame(replication_results).to_excel(save_location, index=False)
                    result["data"] = replication_results
                else:
                    result["cancelled"] = True
                    
            except Exception as e:
                result["error"] = str(e)
        
        # Start the replication in a separate thread
        thread = threading.Thread(target=replication_worker)
        thread.daemon = True
        thread.start()
        
        # Wait for completion or cancellation
        def check_completion():
            if thread.is_alive():
                root.after(100, check_completion)  # Check again in 100ms
            else:
                progress_dialog.close()
                
                if result["cancelled"]:
                    messagebox.showinfo("Cancelled", "Replication operation was cancelled.")
                elif result["error"]:
                    messagebox.showerror("Error", f"An error occurred:\n{result['error']}")
                else:
                    message = f"Scan and Copy completed successfully.\nReport has been saved to:\n{save_location}"
                    messagebox.showinfo("Completed", message)
                    
                root.destroy()
        
        root.after(100, check_completion)

    root.mainloop()
