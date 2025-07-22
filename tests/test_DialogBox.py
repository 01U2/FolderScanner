import pytest
from tkinter import filedialog
from src.getFolders import select_folder, select_save_location

def test_select_folder_success(monkeypatch):
    monkeypatch.setattr(filedialog, "askdirectory", lambda title: "/tmp")
    assert select_folder("title") == "/tmp"

def test_select_folder_cancel(monkeypatch):
    monkeypatch.setattr(filedialog, "askdirectory", lambda title: "")
    with pytest.raises(FileNotFoundError):
        select_folder("title")

def test_select_save_location_success(monkeypatch):
    monkeypatch.setattr(filedialog, "asksaveasfilename", lambda **kw: "/tmp/out.xlsx")
    assert select_save_location("title").endswith(".xlsx")

def test_select_save_location_cancel(monkeypatch):
    monkeypatch.setattr(filedialog, "asksaveasfilename", lambda **kw: "")
    with pytest.raises(FileNotFoundError):
        select_save_location("title")