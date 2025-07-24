import pandas as pd
from tkinter import filedialog

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
