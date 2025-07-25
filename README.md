# 📁 Folder Scanner & Structure Replicator

This Python application lets users scan a selected folder and its subdirectories, output the structure to an Excel file, and optionally replicate that structure to a new destination.

## 🚀 Features

- Interactive **Tkinter GUI** for folder selection and guidance
- Exports folder structure with details:
  - Name
  - Path
  - Parent directory
  - Depth from root
- Optional replication of directory structure to a chosen location
- Saves results to a clean, formatted Excel file (`.xlsx`)

## 🧱 Requirements

Install dependencies using `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 🧱 generate installer

```
pip install pyinstaller
pyinstaller --onefile --windowed installer.py
```

## Upcoming Features

- [ ] Dark mode for the GUI
- [ ] Integrate error reporting
