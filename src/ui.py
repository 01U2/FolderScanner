import tkinter as tk
from tkinter import messagebox
import pandas as pd
from file_io import select_folder, select_save_location, save_to_excel
from scanner import collect_folders_and_files
from replicator import replicate_folder_structure

def ask_user_choice():
    root = tk.Tk()
    root.title("Folder and File Scanner")
    root.geometry("600x350")
    root.eval('tk::PlaceWindow . center')

    # ---------- Main Instructions ----------
    guide_text = (
        "Welcome to Folder and File Scanner!\n\n"
        "• Click 'Scan' to select a folder and export its structure to Excel.\n"
        "• Check 'Include Files' to scan specific file types.\n"
        "• Check 'Replicate Structure' to copy the folder layout elsewhere.\n\n"
        "Report issues to olufemi.akinwumi@wsp.com."
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

    # Replicate checkbox
    tk.Checkbutton(options_frame, text="Replicate Structure", variable=replicate_var, anchor="w").pack(anchor="w", pady=2)
    # Include files checkbox
    tk.Checkbutton(options_frame, text="Include Files", variable=include_files_var, anchor="w").pack(anchor="w", pady=2)

    # ---------- Extensions Entry (initially hidden) ----------
    extensions_frame = tk.Frame(root)
    tk.Label(extensions_frame, text="File extensions to include (e.g. .pdf, .docx):").pack(anchor="w")
    tk.Entry(extensions_frame, textvariable=extensions_var, width=50).pack(anchor="w", pady=2)

    # ---------- Scan Button ----------
    tk.Button(root, text="Scan", command=lambda: start_scan(), width=20, height=2).pack(pady=20)

    # ---------- Logic for Scanning ----------
    def start_scan():
        try:
            source_folder = select_folder("Select Folder to Scan")
            if not source_folder:
                raise FileNotFoundError("No folder selected.")

            save_location = select_save_location("Select Excel Save Location")
            if not save_location:
                raise FileNotFoundError("No save location selected.")

            include_files = include_files_var.get()
            extensions = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()] if include_files else None

            data = collect_folders_and_files(source_folder, include_files, extensions)

            if replicate_var.get():
                dest_folder = select_folder("Select Destination for Replication")
                if not dest_folder:
                    raise FileNotFoundError("No replication destination selected.")
                replication_results = replicate_folder_structure(source_folder, dest_folder)
                pd.DataFrame(replication_results).to_excel(save_location, index=False)
            else:
                save_to_excel(data, save_location)

            messagebox.showinfo("Completed", "Scan completed successfully.")

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            root.destroy()

    root.mainloop()
