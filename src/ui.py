import tkinter as tk
from tkinter import messagebox
import pandas as pd
from src.file_io import select_folder, select_save_location, save_to_excel
from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.duplicate_detector import find_duplicates, format_duplicate_results, get_duplicate_statistics
import sys
import os

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
        "• Check 'Detect Duplicates' to find duplicate files based on content.\n"
        "• Check 'Replicate Structure' to copy the folder (and files) layout elsewhere.\n"
        "• Click 'Scan' to start the activity.\n\n"

    )
    tk.Label(root, text=guide_text, justify="left", wraplength=580, fg="blue").pack(pady=10)

    # ---------- Options Frame ----------
    options_frame = tk.Frame(root)
    options_frame.pack(fill="x", padx=20)

    include_files_var = tk.BooleanVar()
    replicate_var = tk.BooleanVar()
    detect_duplicates_var = tk.BooleanVar()
    extensions_var = tk.StringVar()

    def toggle_extensions_input(*args):
        if include_files_var.get():
            extensions_frame.pack(fill="x", padx=20, pady=5)
        else:
            extensions_frame.forget()
            # If files are not included, disable duplicate detection
            if not include_files_var.get():
                detect_duplicates_var.set(False)

    def toggle_duplicate_detection(*args):
        if detect_duplicates_var.get() and not include_files_var.get():
            # Force include files if duplicate detection is enabled
            include_files_var.set(True)

    include_files_var.trace_add("write", toggle_extensions_input)
    detect_duplicates_var.trace_add("write", toggle_duplicate_detection)

    # Include files checkbox
    tk.Checkbutton(options_frame, text="Include Files", variable=include_files_var, anchor="w").pack(anchor="w", pady=2)
    # Detect duplicates checkbox
    tk.Checkbutton(options_frame, text="Detect Duplicates", variable=detect_duplicates_var, anchor="w").pack(anchor="w", pady=2)
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
            detect_duplicates = detect_duplicates_var.get()
            extensions = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()] if include_files else None
        
            if replicate_var.get():
                dest_folder = select_folder("Select Destination for Replication")
                replication_results = replicate_folder_structure(source_folder, dest_folder, include_files, extensions)
                pd.DataFrame(replication_results).to_excel(save_location, index=False)
                message = f"Scan and Copy completed successfully.\nReport has been saved to:\n{save_location}"
            else:
                data = collect_folders_and_files(source_folder, include_files, extensions)
                
                if detect_duplicates and include_files:
                    # Find duplicates and format results
                    duplicates = find_duplicates(data)
                    if duplicates:
                        duplicate_results = format_duplicate_results(duplicates)
                        stats = get_duplicate_statistics(duplicates)
                        
                        # Save duplicate results
                        save_to_excel(duplicate_results, save_location)
                        
                        message = (
                            f"Duplicate detection completed successfully.\n"
                            f"Found {stats['total_duplicate_files']} duplicate files in {stats['total_groups']} groups.\n"
                            f"Potential space saved: {stats['total_wasted_space_mb']} MB\n"
                            f"Report has been saved to:\n{save_location}"
                        )
                    else:
                        # No duplicates found, save regular scan
                        save_to_excel(data, save_location)
                        message = f"No duplicate files found.\nRegular scan report has been saved to:\n{save_location}"
                else:
                    # Regular scan without duplicate detection
                    save_to_excel(data, save_location)
                    message = f"Scan completed successfully.\nReport has been saved to:\n{save_location}"

            messagebox.showinfo("Completed", message)
                

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            root.destroy()

    root.mainloop()
