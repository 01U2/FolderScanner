import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from shutil import copytree, Error as ShutilError

def collect_folders(root_folder):
    folder_data = []
    for dirpath, dirnames, _ in os.walk(root_folder):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            parent = os.path.basename(dirpath)
            depth = len(Path(full_path).parts) - len(Path(root_folder).parts)
            folder_data.append({
                'Name': dirname,
                'Path': full_path,
                'Parent': parent,
                'Depth': depth
            })
    return folder_data

def save_to_excel(data, file_path):
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

def select_folder(title):
    folder_selected = filedialog.askdirectory(title=title)
    if not folder_selected:
        raise FileNotFoundError("No folder selected.")
    return folder_selected

def select_save_location(title):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title=title)
    if not file_path:
        raise FileNotFoundError("No save location selected.")
    return file_path

def replicate_folder_structure(source, destination):
    replicated = []
    for dirpath, dirnames, _ in os.walk(source):
        for dirname in dirnames:
            source_path = os.path.join(dirpath, dirname)
            relative_path = os.path.relpath(source_path, source)
            dest_path = os.path.join(destination, relative_path)
            try:
                os.makedirs(dest_path, exist_ok=True)
                status = 'Replicated'
            except Exception as e:
                status = f'Failed: {e}'
            replicated.append({
                'Name': dirname,
                'Source Path': source_path,
                'Destination Path': dest_path,
                'Status': status
            })
    return replicated

def ask_user_choice():
    root = tk.Tk()
    root.title("Folder Scanner")
    root.geometry("600x300")
    root.eval('tk::PlaceWindow . center')
    # Add a guide/instruction label
    guide_text = (
        "Welcome to Folder Scanner!\n"
        "Folder scanner simply parses the selected folder and its subfolders\n\n"
        "Click 'Scan' to select a folder and export its structure to Excel.\n"
        "Check 'Replicate Structure' if you want to copy the scanned folder structure to another location.\n"
        "You will be prompted to select the destination and save the Excel report.\n\n\n"
        
        "please report issues to 01U."
    )
    tk.Label(root, text=guide_text, justify="left", wraplength=580, fg="blue").pack(pady=10)

    replicate_var = tk.BooleanVar()

    def start_scan():
        try:
            source_folder = select_folder("Select Folder to Scan")
            save_location = select_save_location("Select Excel Save Location")
            folder_data = collect_folders(source_folder)

            if replicate_var.get():
                dest_folder = select_folder("Select Destination for Replication")
                replication_results = replicate_folder_structure(source_folder, dest_folder)
                df = pd.DataFrame(replication_results)
                df.to_excel(save_location, index=False)
            else:
                save_to_excel(folder_data, save_location)

            messagebox.showinfo("Completed", "Operation completed successfully.")
        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            root.destroy()

    tk.Checkbutton(root, text="Replicate Structure", variable=replicate_var).pack(pady=10)
    tk.Button(root, text="Scan", command=start_scan, width=20, height=2).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    ask_user_choice()
