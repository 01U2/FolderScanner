import tkinter as tk
from tkinter import messagebox
import pandas as pd
from src.file_io import select_folder, select_save_location, save_to_excel
from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
import sys
import os

class FolderScannerApp:
    def __init__(self, root):
        self.root = root
        root.title("Folder and File Scanner")
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # PyInstaller's temp path
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "icon", "folderScanner.ico")
        try:
            root.iconbitmap(icon_path)
        except tk.TclError:
            pass  # Continue without icon if not found
        root.geometry("600x350")
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
        tk.Label(root, text=guide_text, justify="left", wraplength=580, fg="blue").pack(pady=self.LABEL_PADDING)

        # ---------- Options Frame ----------
        options_frame = tk.Frame(root)
        options_frame.pack(fill="x", padx=20)

        self.include_files_var = tk.BooleanVar()
        self.replicate_var = tk.BooleanVar()
        self.extensions_var = tk.StringVar()

        def toggle_extensions_input():
            if self.include_files_var.get():
                extensions_frame.pack(fill="x", padx=20, pady=5)
            else:
                extensions_frame.forget()

        self.include_files_var.trace_add("write", lambda *args: toggle_extensions_input())

        # Include files checkbox
        tk.Checkbutton(options_frame, text="Include Files", variable=self.include_files_var, anchor="w").pack(anchor="w", pady=2)
        # Replicate checkbox
        tk.Checkbutton(options_frame, text="Replicate Structure", variable=self.replicate_var, anchor="w").pack(anchor="w", pady=2)
        
        # ---------- Extensions Entry (initially hidden) ----------
        extensions_frame = tk.Frame(root)
        tk.Label(extensions_frame, text="Provide file extensions, seperated by ',' (example: .pdf, .docx)").pack(anchor="w")
        tk.Entry(extensions_frame, textvariable=self.extensions_var, width=50).pack(anchor="w", pady=2)

        # ---------- Scan Button ----------
        tk.Button(root, text="Scan", command=lambda: self.start_scan(), width=20, height=2).pack(pady=20)

    # ---------- Logic for Scanning ----------
    def start_scan(self):
        try:
            source_folder = select_folder("Select Folder to Scan")
            save_location = select_save_location()

            include_files = self.include_files_var.get()
            extensions = [ext.strip() for ext in self.extensions_var.get().split(',') if ext.strip()] if include_files else None
        
            if self.replicate_var.get():
                dest_folder = select_folder("Select Destination for Replication")
                replication_results = replicate_folder_structure(source_folder, dest_folder, include_files, extensions)
                pd.DataFrame(replication_results).to_excel(save_location, index=False)
            else:
                data = collect_folders_and_files(source_folder, include_files, extensions)
                save_to_excel(data, save_location)

            
            message = (
                        f"Scan and Copy completed successfully.\nReport has been saved to:\n{save_location}"
                        if self.replicate_var.get()
                        else f"Scan completed successfully.\nReport has been saved to:\n{save_location}"
            )
            messagebox.showinfo("Completed", message)
                

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            self.root.destroy()

def ask_user_choice():
    root = tk.Tk()
    FolderScannerApp(root)
    root.mainloop()
