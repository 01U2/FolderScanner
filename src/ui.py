import tkinter as tk
from tkinter import messagebox
import pandas as pd
from src.file_io import select_folder, select_save_location, save_to_excel
from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.theme_manager import ThemeManager
import sys
import os

def ask_user_choice():
    root = tk.Tk()
    root.title("Folder and File Scanner")
    
    # Initialize theme manager
    theme_manager = ThemeManager()
    
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller's temp path
    else:
        base_path = os.path.abspath(".")

    try:
        icon_path = os.path.join(base_path, "icon", "folderScanner.ico")
        root.iconbitmap(icon_path)
    except:
        pass  # Icon file may not exist in all environments
        
    root.geometry("600x450")  # Slightly taller for theme toggle
    root.eval('tk::PlaceWindow . center')
    
    # Apply initial theme to root
    theme_manager.apply_theme_to_widget(root, 'root')

    # ---------- Theme Toggle Frame ----------
    theme_frame = tk.Frame(root)
    theme_frame.pack(fill="x", padx=20, pady=(10, 5))
    theme_manager.apply_theme_to_widget(theme_frame, 'frame')
    
    current_theme_text = f"Theme: {theme_manager.current_theme.title()}"
    theme_label = tk.Label(theme_frame, text=current_theme_text)
    theme_label.pack(side="left")
    theme_manager.apply_theme_to_widget(theme_label, 'label')
    
    def toggle_theme():
        new_theme = theme_manager.toggle_theme()
        theme_label.config(text=f"Theme: {new_theme.title()}")
        apply_theme_to_all_widgets()
    
    theme_button = tk.Button(theme_frame, text="🌓 Toggle Theme", command=toggle_theme, width=15)
    theme_button.pack(side="right")
    theme_manager.apply_theme_to_widget(theme_button, 'button')

    # ---------- Main Instructions ----------
    guide_text = (
        "Welcome to Folder and File Scanner!\n"
        "It simply allows scanning, reporting and replicating folder contents.\n\n"
        "• Check 'Include Files' to include files in the scan.\n"
        "• Use the Filter text to filter by specific file types.\n"
        "• Check 'Replicate Structure' to copy the folder (and files) layout elsewhere.\n"
        "• Click 'Scan' to start the activity.\n\n"

    )
    instructions_label = tk.Label(root, text=guide_text, justify="left", wraplength=580)
    instructions_label.pack(pady=10)
    theme_manager.apply_theme_to_widget(instructions_label, 'label')

    # ---------- Options Frame ----------
    options_frame = tk.Frame(root)
    options_frame.pack(fill="x", padx=20)
    theme_manager.apply_theme_to_widget(options_frame, 'frame')

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
    include_files_checkbox = tk.Checkbutton(options_frame, text="Include Files", variable=include_files_var, anchor="w")
    include_files_checkbox.pack(anchor="w", pady=2)
    theme_manager.apply_theme_to_widget(include_files_checkbox, 'checkbutton')
    
    # Replicate checkbox
    replicate_checkbox = tk.Checkbutton(options_frame, text="Replicate Structure", variable=replicate_var, anchor="w")
    replicate_checkbox.pack(anchor="w", pady=2)
    theme_manager.apply_theme_to_widget(replicate_checkbox, 'checkbutton')
    
    # ---------- Extensions Entry (initially hidden) ----------
    extensions_frame = tk.Frame(root)
    theme_manager.apply_theme_to_widget(extensions_frame, 'frame')
    
    extensions_label = tk.Label(extensions_frame, text="Provide file extensions, seperated by ',' (example: .pdf, .docx)")
    extensions_label.pack(anchor="w")
    theme_manager.apply_theme_to_widget(extensions_label, 'label')
    
    extensions_entry = tk.Entry(extensions_frame, textvariable=extensions_var, width=50)
    extensions_entry.pack(anchor="w", pady=2)
    theme_manager.apply_theme_to_widget(extensions_entry, 'entry')

    # ---------- Scan Button ----------
    scan_button = tk.Button(root, text="Scan", command=lambda: start_scan(), width=20, height=2)
    scan_button.pack(pady=20)
    theme_manager.apply_theme_to_widget(scan_button, 'button')

    # Function to apply theme to all widgets
    def apply_theme_to_all_widgets():
        theme_manager.apply_theme_to_widget(root, 'root')
        theme_manager.apply_theme_to_widget(theme_frame, 'frame')
        theme_manager.apply_theme_to_widget(theme_label, 'label')
        theme_manager.apply_theme_to_widget(theme_button, 'button')
        theme_manager.apply_theme_to_widget(instructions_label, 'label')
        theme_manager.apply_theme_to_widget(options_frame, 'frame')
        theme_manager.apply_theme_to_widget(include_files_checkbox, 'checkbutton')
        theme_manager.apply_theme_to_widget(replicate_checkbox, 'checkbutton')
        theme_manager.apply_theme_to_widget(extensions_frame, 'frame')
        theme_manager.apply_theme_to_widget(extensions_label, 'label')
        theme_manager.apply_theme_to_widget(extensions_entry, 'entry')
        theme_manager.apply_theme_to_widget(scan_button, 'button')

    # ---------- Logic for Scanning ----------
    def start_scan():
        try:
            source_folder = select_folder("Select Folder to Scan")
            save_location = select_save_location()

            include_files = include_files_var.get()
            extensions = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()] if include_files else None
        
            if replicate_var.get():
                dest_folder = select_folder("Select Destination for Replication")
                replication_results = replicate_folder_structure(source_folder, dest_folder, include_files, extensions)
                pd.DataFrame(replication_results).to_excel(save_location, index=False)
            else:
                data = collect_folders_and_files(source_folder, include_files, extensions)
                save_to_excel(data, save_location)

            
            message = (
                        f"Scan and Copy completed successfully.\nReport has been saved to:\n{save_location}"
                        if replicate_var.get()
                        else f"Scan completed successfully.\nReport has been saved to:\n{save_location}"
            )
            messagebox.showinfo("Completed", message)
                

        except FileNotFoundError:
            messagebox.showwarning("Cancelled", "Operation cancelled by the user.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            root.destroy()

    root.mainloop()
