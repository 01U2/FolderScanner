import tkinter as tk
from tkinter import messagebox
import pandas as pd
from src.file_io import select_folder, select_save_location, save_to_excel
from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.duplicate_detector import find_duplicates, format_duplicate_results, get_duplicate_statistics
import sys
import os


class FolderScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder and File Scanner")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "icon", "folderScanner.ico")
        try:
            root.iconbitmap(icon_path)
        except tk.TclError:
            pass  # No icon fallback

        root.geometry("600x450")
        root.eval('tk::PlaceWindow . center')

        # ---------- Guide Text ----------
        guide_text = (
            "Welcome to Folder and File Scanner!\n"
            "It allows scanning, reporting, and replicating folder contents.\n\n"
            "• Check 'Include Files' to include files in the scan.\n"
            "• Use the Filter text to filter by specific file types.\n"
            "• Exclude specific folders by listing their names (comma-separated).\n"
            "• Check 'Replicate Structure' to copy the folder layout elsewhere.\n"
            "• Click 'Scan' to start.\n"
        )
        tk.Label(root, text=guide_text, justify="left", wraplength=580, fg="blue").pack(pady=10)

        # ---------- Variables ----------
        self.include_files_var = tk.BooleanVar()
        self.exclude_folders_var = tk.BooleanVar()
        self.replicate_var = tk.BooleanVar()
        self.extensions_var = tk.StringVar()
        self.excluded_folders_var = tk.StringVar()
        self.detect_duplicates_var = tk.BooleanVar()

        # ---------- Options Frame ----------
        options_frame = tk.Frame(root)
        options_frame.pack(fill="x", padx=20)

        # ---------- Checkboxes ----------
        tk.Checkbutton(options_frame, text="Include File(s)", variable=self.include_files_var).pack(anchor="w", pady=2)
        tk.Checkbutton(options_frame, text="Exclude Folder(s)", variable=self.exclude_folders_var).pack(anchor="w", pady=2)
        tk.Checkbutton(options_frame, text="Detect Duplicates", variable=detect_duplicates_var, anchor="w").pack(anchor="w", pady=2)
        tk.Checkbutton(options_frame, text="Replicate Structure", variable=self.replicate_var).pack(anchor="w", pady=2)

        # ---------- Toggle Input Fields ----------
        self.toggle_frame = tk.Frame(root)
        self.toggle_frame.pack(fill="x", padx=20, pady=5)

        self.extensions_frame = tk.Frame(self.toggle_frame)
        tk.Label(self.extensions_frame, text="File extensions (e.g. .pdf, .docx)").pack(anchor="w")
        tk.Entry(self.extensions_frame, textvariable=self.extensions_var, width=50).pack(anchor="w", pady=2)
        self.extensions_frame.pack_forget()

        self.folders_frame = tk.Frame(self.toggle_frame)
        tk.Label(self.folders_frame, text="Exclude folders (e.g. temp, cache)").pack(anchor="w")
        tk.Entry(self.folders_frame, textvariable=self.excluded_folders_var, width=50).pack(anchor="w", pady=2)
        self.folders_frame.pack_forget()
        
        self.folders_frame = tk.Frame(self.toggle_frame)
        tk.Label(self.folders_frame, text="Document Duplicates?").pack(anchor="w")
        tk.Entry(self.folders_frame, textvariable=self.detect_duplicates_var, width=50).pack(anchor="w", pady=2)
        self.folders_frame.pack_forget()
        
        

        # ---------- Toggle Events ----------
        self.include_files_var.trace_add("write", self.toggle_extensions_input)
        self.exclude_folders_var.trace_add("write", self.toggle_folders_input)
        self.detect_duplicates_var.trace_add("write", self.toggle_duplicate_detection)

        # ---------- Scan Button ----------
        tk.Button(root, text="Scan", command=self.start_scan, width=20, height=2).pack(pady=20)

    def toggle_extensions_input(self, *args):
        if self.include_files_var.get():
            self.extensions_frame.pack(fill="x", pady=5)
        else:
            self.extensions_frame.pack_forget()

    def toggle_folders_input(self, *args):
        if self.exclude_folders_var.get():
            self.folders_frame.pack(fill="x", pady=5)
        else:
            self.folders_frame.pack_forget()

    def start_scan(self):
        try:
            source_folder = select_folder("Select Folder to Scan")

            include_files = self.include_files_var.get()
            detect_duplicates = detect_duplicates_var.get()
            extensions = [e.strip() for e in self.extensions_var.get().split(',') if e.strip()] if include_files else None
            excluded_folders = [f.strip() for f in self.excluded_folders_var.get().split(',') if f.strip()] if self.exclude_folders_var.get() else None

            if self.replicate_var.get():
                save_location = select_save_location(report_type="replication")
                dest_folder = select_folder("Select Destination for Replication")
                results = replicate_folder_structure(
                    source_folder, dest_folder, include_files, extensions, excluded_folders
                )
                pd.DataFrame(results).to_excel(save_location, index=False)
            else:
                data = collect_folders_and_files(source_folder, include_files, extensions)
                
                if detect_duplicates and include_files:
                    # Find duplicates and format results
                    duplicates = find_duplicates(data)
                    if duplicates:
                        save_location = select_save_location(report_type="duplicates")
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
                        save_location = select_save_location(report_type="structure")
                        save_to_excel(data, save_location)
                        message = f"No duplicate files found.\nRegular scan report has been saved to:\n{save_location}"
                else:
                    # Regular scan without duplicate detection
                    save_location = select_save_location(report_type="structure")
                    save_to_excel(data, save_location)
                    message = f"Scan completed successfully.\nReport has been saved to:\n{save_location}"

            messagebox.showinfo("Completed", message)
                

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            self.root.destroy()


def ask_user_choice():
    root = tk.Tk()
    FolderScannerApp(root)
    root.mainloop()
