import unittest
import tempfile
import os
import shutil
import pandas as pd
from pathlib import Path

from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.file_io import save_to_excel


class TestFolderScanner(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "subfolder"))
        os.makedirs(os.path.join(self.test_dir, "temp"))
        os.makedirs(os.path.join(self.test_dir, "cache"))
        os.makedirs(os.path.join(self.test_dir, "subfolder", "nested"))
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(self.test_dir, "file2.pdf"), "w") as f:
            f.write("PDF content")
        with open(os.path.join(self.test_dir, "subfolder", "file3.docx"), "w") as f:
            f.write("DOCX content")
        with open(os.path.join(self.test_dir, "temp", "temp_file.txt"), "w") as f:
            f.write("Temp content")
        with open(os.path.join(self.test_dir, "cache", "cache_file.txt"), "w") as f:
            f.write("Cache content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scan_folders_only(self):
        result = collect_folders_and_files(self.test_dir, include_files=False)
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        self.assertIn("subfolder", folder_names)
        self.assertTrue(all(item['Type'] == 'Folder' for item in result))

    def test_scan_with_files(self):
        result = collect_folders_and_files(self.test_dir, include_files=True)
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.pdf", file_names)
        self.assertIn("file3.docx", file_names)

    def test_scan_with_extension_filter(self):
        result = collect_folders_and_files(self.test_dir, include_files=True, extensions=[".pdf"])
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        self.assertIn("file2.pdf", file_names)
        self.assertNotIn("file1.txt", file_names)
        self.assertNotIn("file3.docx", file_names)

    def test_scan_with_excluded_folders(self):
        result = collect_folders_and_files(self.test_dir, include_files=False, excluded_folders=["temp", "cache"])
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        self.assertIn("subfolder", folder_names)
        self.assertIn("nested", folder_names)  # Should include nested folder in allowed subfolder
        self.assertNotIn("temp", folder_names)
        self.assertNotIn("cache", folder_names)

    def test_scan_with_excluded_folders_case_insensitive(self):
        result = collect_folders_and_files(self.test_dir, include_files=False, excluded_folders=["TEMP", "Cache"])
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        self.assertIn("subfolder", folder_names)
        self.assertNotIn("temp", folder_names)
        self.assertNotIn("cache", folder_names)

    def test_scan_with_excluded_folders_and_files(self):
        result = collect_folders_and_files(self.test_dir, include_files=True, excluded_folders=["temp", "cache"])
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        
        # Should include files from allowed folders
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.pdf", file_names)
        self.assertIn("file3.docx", file_names)
        
        # Should not include files from excluded folders
        self.assertNotIn("temp_file.txt", file_names)
        self.assertNotIn("cache_file.txt", file_names)
        
        # Should include allowed folders but not excluded ones
        self.assertIn("subfolder", folder_names)
        self.assertNotIn("temp", folder_names)
        self.assertNotIn("cache", folder_names)


class TestFolderReplicator(unittest.TestCase):

    def setUp(self):
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.source_dir, "subfolder"))
        os.makedirs(os.path.join(self.source_dir, "temp"))
        os.makedirs(os.path.join(self.source_dir, "cache"))
        with open(os.path.join(self.source_dir, "file1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(self.source_dir, "subfolder", "file2.pdf"), "w") as f:
            f.write("PDF content")
        with open(os.path.join(self.source_dir, "temp", "temp_file.txt"), "w") as f:
            f.write("Temp content")
        with open(os.path.join(self.source_dir, "cache", "cache_file.txt"), "w") as f:
            f.write("Cache content")

    def tearDown(self):
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.dest_dir)

    def test_replicate_folders_only(self):
        result = replicate_folder_structure(self.source_dir, self.dest_dir, include_files=False)
        folder_entries = [item for item in result if item['Type'] == 'Folder']
        file_entries = [item for item in result if item['Type'] == 'File']
        self.assertGreaterEqual(len(folder_entries), 1)
        self.assertEqual(len(file_entries), 0)

    def test_replicate_with_files(self):
        result = replicate_folder_structure(self.source_dir, self.dest_dir, include_files=True)
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.pdf", file_names)

    def test_replicate_with_extension_filter(self):
        result = replicate_folder_structure(self.source_dir, self.dest_dir, include_files=True, extensions=[".pdf"])
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        self.assertIn("file2.pdf", file_names)
        self.assertNotIn("file1.txt", file_names)

    def test_replicate_with_excluded_folders(self):
        result = replicate_folder_structure(self.source_dir, self.dest_dir, include_files=False, excluded_folders=["temp", "cache"])
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        self.assertIn("subfolder", folder_names)
        self.assertNotIn("temp", folder_names)
        self.assertNotIn("cache", folder_names)

    def test_replicate_with_excluded_folders_and_files(self):
        result = replicate_folder_structure(self.source_dir, self.dest_dir, include_files=True, excluded_folders=["temp", "cache"])
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        
        # Should include files from allowed folders
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.pdf", file_names)
        
        # Should not include files from excluded folders
        self.assertNotIn("temp_file.txt", file_names)
        self.assertNotIn("cache_file.txt", file_names)
        
        # Should include allowed folders but not excluded ones
        self.assertIn("subfolder", folder_names)
        self.assertNotIn("temp", folder_names)
        self.assertNotIn("cache", folder_names)


class TestFileIO(unittest.TestCase):

    def test_save_to_excel(self):
        data = [
            {"Type": "Folder", "Name": "TestFolder", "Path": "/tmp/TestFolder", "Extension": ""},
            {"Type": "File", "Name": "file.txt", "Path": "/tmp/file.txt", "Extension": ".txt"}
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            save_to_excel(data, tmp_path)
            df = pd.read_excel(tmp_path, engine="openpyxl")
            self.assertEqual(len(df), 2)
            self.assertIn("Name", df.columns)
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
