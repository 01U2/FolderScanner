import pandas as pd
from tkinter import filedialog
from datetime import datetime
from pathlib import Path
import os

def save_to_excel(data, file_path):
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

def select_folder(title):
    folder_selected = filedialog.askdirectory(title=title)
    if not folder_selected:
        raise FileNotFoundError("No folder selected.")
    return folder_selected

def select_save_location(report_type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        desktop = str(Path.home() / "Documents")
        if not os.path.exists(desktop):
            desktop = str(Path.home() / "Desktop")
        if not os.path.exists(desktop):
            desktop = str(Path.home())
    except:
        desktop = os.getcwd()
    
    if report_type == "duplicates":
        filename = f"Duplicate_Files_Report_{timestamp}.xlsx"
    else:
        filename = f"Folder_Structure_{timestamp}.xlsx"
        
    file_path = os.path.join(desktop, filename)
    return file_path

    



