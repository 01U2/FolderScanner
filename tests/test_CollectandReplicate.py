import os
import pandas as pd
import tempfile
import pytest
from pathlib import Path

from src.getFolders import collect_folders, replicate_folder_structure

def test_collect_folders_empty(tmp_path):
    # empty directory ⇒ no folder entries
    data = collect_folders(str(tmp_path))
    assert isinstance(data, list)
    assert data == []

def test_collect_folders_nested(tmp_path):
    # create nested folders
    root = tmp_path / "root"
    sub1 = root / "sub1"
    sub2 = sub1 / "sub2"
    sub2.mkdir(parents=True)
    # collect
    data = collect_folders(str(root))
    paths = {item["Path"] for item in data}
    assert str(sub1) in paths
    assert str(sub2) in paths
    # depth calculation
    depth_map = {item["Name"]: item["Depth"] for item in data}
    assert depth_map["sub1"] == 1
    assert depth_map["sub2"] == 2

def test_replicate_folder_structure_success(tmp_path):
    # source with two levels and a file inside each
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src / "A/B").mkdir(parents=True)
    results = replicate_folder_structure(str(src), str(dst))
    # check that each dirname appears once and dest folder was created
    names = {r["Name"] for r in results}
    assert names == {"A", "B"}
    for entry in results:
        assert os.path.isdir(entry["Destination Path"])
        assert entry["Status"] == "Replicated"

def test_replicate_folder_structure_permission_error(tmp_path, monkeypatch):
    # simulate os.makedirs raising
    src = tmp_path / "src2"
    dst = tmp_path / "dst2"
    (src / "X").mkdir(parents=True)
    def fake_makedirs(path, exist_ok):
        raise PermissionError("denied")
    monkeypatch.setattr("src.getFolders.os.makedirs", fake_makedirs)
    results = replicate_folder_structure(str(src), str(dst))
    assert results[0]["Status"].startswith("Failed:")
