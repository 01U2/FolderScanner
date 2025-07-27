import tkinter as tk
from tkinter import messagebox
import pandas as pd
from src.file_io import select_folder, select_save_location, save_to_excel
from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.comparator import compare_folders, get_comparison_summary
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
        "It allows scanning, reporting, replicating, and comparing folder contents.\n\n"
        "• Check 'Include Files' to include files in the scan.\n"
        "• Use the Filter text to filter by specific file types.\n"
        "• Check 'Replicate Structure' to copy the folder (and files) layout elsewhere.\n"
        "• Check 'Compare Folders' to compare two directories and highlight differences.\n"
        "• Click 'Start' to begin the selected operation.\n\n"

    )
    tk.Label(root, text=guide_text, justify="left", wraplength=580, fg="blue").pack(pady=10)

    # ---------- Options Frame ----------
    options_frame = tk.Frame(root)
    options_frame.pack(fill="x", padx=20)

    include_files_var = tk.BooleanVar()
    replicate_var = tk.BooleanVar()
    compare_var = tk.BooleanVar()
    extensions_var = tk.StringVar()

    def toggle_extensions_input(*args):
        if include_files_var.get():
            extensions_frame.pack(fill="x", padx=20, pady=5)
        else:
            extensions_frame.forget()
    
    def toggle_mutually_exclusive(*args):
        # Make replicate and compare mutually exclusive
        if replicate_var.get() and compare_var.get():
            if args[0] == 'replicate':
                compare_var.set(False)
            else:
                replicate_var.set(False)

    include_files_var.trace_add("write", toggle_extensions_input)
    replicate_var.trace_add("write", lambda *args: toggle_mutually_exclusive('replicate'))
    compare_var.trace_add("write", lambda *args: toggle_mutually_exclusive('compare'))

    # Include files checkbox
    tk.Checkbutton(options_frame, text="Include Files", variable=include_files_var, anchor="w").pack(anchor="w", pady=2)
    # Replicate checkbox
    tk.Checkbutton(options_frame, text="Replicate Structure", variable=replicate_var, anchor="w").pack(anchor="w", pady=2)
    # Compare checkbox
    tk.Checkbutton(options_frame, text="Compare Folders", variable=compare_var, anchor="w").pack(anchor="w", pady=2)
    
    # ---------- Extensions Entry (initially hidden) ----------
    extensions_frame = tk.Frame(root)
    tk.Label(extensions_frame, text="Provide file extensions, seperated by ',' (example: .pdf, .docx)").pack(anchor="w")
    tk.Entry(extensions_frame, textvariable=extensions_var, width=50).pack(anchor="w", pady=2)

    # ---------- Start Button ----------
    tk.Button(root, text="Start", command=lambda: start_operation(), width=20, height=2).pack(pady=20)

    # ---------- Logic for Operations ----------
    def start_operation():
        try:
            include_files = include_files_var.get()
            extensions = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()] if include_files else None
            
            if compare_var.get():
                # Folder comparison mode
                folder1 = select_folder("Select First Folder to Compare")
                folder2 = select_folder("Select Second Folder to Compare")
                save_location = select_save_location("Folder_Comparison")
                
                # Perform comparison
                comparison_results = compare_folders(folder1, folder2)
                summary = get_comparison_summary(comparison_results)
                
                # Create a comprehensive report with summary and details
                summary_df = pd.DataFrame([summary])
                comparison_df = pd.DataFrame(comparison_results)
                
                # Save to Excel with multiple sheets
                with pd.ExcelWriter(save_location, engine='openpyxl') as writer:
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    comparison_df.to_excel(writer, sheet_name='Detailed Comparison', index=False)
                
                message = f"Folder comparison completed successfully.\nFound {summary['Total Items']} items.\nReport saved to:\n{save_location}"
                messagebox.showinfo("Comparison Complete", message)
                
            elif replicate_var.get():
                # Replication mode
                source_folder = select_folder("Select Folder to Scan")
                dest_folder = select_folder("Select Destination for Replication")
                save_location = select_save_location("Folder_Replication")
                
                replication_results = replicate_folder_structure(source_folder, dest_folder, include_files, extensions)
                pd.DataFrame(replication_results).to_excel(save_location, index=False)
                
                message = f"Scan and Copy completed successfully.\nReport has been saved to:\n{save_location}"
                messagebox.showinfo("Replication Complete", message)
            else:
                # Standard scanning mode
                source_folder = select_folder("Select Folder to Scan")
                save_location = select_save_location("Folder_Structure")
                
                data = collect_folders_and_files(source_folder, include_files, extensions)
                save_to_excel(data, save_location)
                
                message = f"Scan completed successfully.\nReport has been saved to:\n{save_location}"
                messagebox.showinfo("Scan Complete", message)

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            root.destroy()

    root.mainloop()
