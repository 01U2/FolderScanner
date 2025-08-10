import unittest
import tempfile
import os
import shutil
import pandas as pd
from pathlib import Path

from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.file_io import save_to_excel
from src.duplicate_detector import get_file_name, find_duplicates, format_duplicate_results, get_duplicate_statistics


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
        
        # Check that Size is included in file entries
        file_entries = [item for item in result if item['Type'] == 'File']
        for file_entry in file_entries:
            self.assertIn('Size', file_entry)
            self.assertIsInstance(file_entry['Size'], int)

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


class TestDuplicateDetector(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create test files with known filenames for filename-based duplicate detection
        self.file1_path = os.path.join(self.test_dir, "document.txt")
        self.duplicate_path = os.path.join(self.test_dir, "subfolder", "document.txt")
        self.file2_path = os.path.join(self.test_dir, "report.txt")
        self.unique_path = os.path.join(self.test_dir, "unique.txt")
        
        # Create subfolder
        os.makedirs(os.path.join(self.test_dir, "subfolder"))
        
        # Create files - same filename in different locations (duplicates)
        with open(self.file1_path, "w") as f:
            f.write("Content A")
        with open(self.duplicate_path, "w") as f:
            f.write("Content B")  # Different content, same filename
            
        # Create files with unique filenames
        with open(self.file2_path, "w") as f:
            f.write("Different content")
        with open(self.unique_path, "w") as f:
            f.write("Unique content here")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_file_name(self):
        # For filename-based detection, function returns lowercase filename
        filename1 = get_file_name(self.file1_path)
        filename2 = get_file_name(self.duplicate_path)
        filename3 = get_file_name(self.file2_path)
        
        # Same filename should produce same result
        self.assertEqual(filename1, filename2)  # Both are "document.txt"
        # Different filename should produce different result
        self.assertNotEqual(filename1, filename3)  # "document.txt" vs "report.txt"
        # Result should be a non-empty string
        self.assertIsInstance(filename1, str)
        self.assertGreater(len(filename1), 0)
        # Should be lowercase
        self.assertEqual(filename1, "document.txt")

    def test_get_file_name_sha256(self):
        # For filename-based detection, algorithm parameter is not supported
        filename = get_file_name(self.file1_path)
        
        # Should return the filename
        self.assertEqual(filename, "document.txt")

    def test_get_file_name_nonexistent_file(self):
        result = get_file_name("/nonexistent/file.txt")
        # Should return the filename even if file doesn't exist (for compatibility)
        self.assertEqual(result, "file.txt")

    def test_find_duplicates(self):
        # Create file list similar to scanner output with filename duplicates
        file_list = [
            {'Type': 'File', 'Name': 'document.txt', 'Path': self.file1_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'document.txt', 'Path': self.duplicate_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'report.txt', 'Path': self.file2_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'unique.txt', 'Path': self.unique_path, 'Extension': '.txt'},
            {'Type': 'Folder', 'Name': 'somefolder', 'Path': '/some/path', 'Extension': ''}
        ]
        
        duplicates = find_duplicates(file_list)
        
        # Should find one group of duplicates (document.txt files)
        self.assertEqual(len(duplicates), 1)
        
        # The duplicate group should have exactly 2 files
        for filename, files in duplicates.items():
            self.assertEqual(len(files), 2)
            self.assertEqual(filename, "document.txt")
            # Check that both files have the same filename
            self.assertEqual(files[0]['File Name'], files[1]['File Name'])
            # Check that files have Size information
            self.assertIn('Size', files[0])
            self.assertIn('Size', files[1])

    def test_find_duplicates_no_duplicates(self):
        # Create file list with unique filenames only
        file_list = [
            {'Type': 'File', 'Name': 'report.txt', 'Path': self.file2_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'unique.txt', 'Path': self.unique_path, 'Extension': '.txt'}
        ]
        
        duplicates = find_duplicates(file_list)
        
        # Should find no duplicates
        self.assertEqual(len(duplicates), 0)

    def test_format_duplicate_results(self):
        # Create a sample duplicate detection result
        duplicates = {
            'document.txt': [
                {'Type': 'File', 'Name': 'document.txt', 'Path': '/path1', 'Extension': '.txt', 'File Name': 'document.txt', 'Size': 100},
                {'Type': 'File', 'Name': 'document.txt', 'Path': '/path2', 'Extension': '.txt', 'File Name': 'document.txt', 'Size': 100}
            ]
        }
        
        results = format_duplicate_results(duplicates)
        
        # Should have 2 entries (one for each duplicate file)
        self.assertEqual(len(results), 2)
        
        # Check structure of results
        for result in results:
            self.assertIn('Duplicate_Group', result)
            self.assertIn('File_Number', result)
            self.assertIn('Total_in_Group', result)
            self.assertIn('Type', result)
            self.assertIn('Name', result)
            self.assertIn('Path', result)
            self.assertIn('Extension', result)
            self.assertIn('Size_Bytes', result)
            self.assertIn('Hash', result)
        
        # Both files should be in the same group
        self.assertEqual(results[0]['Duplicate_Group'], results[1]['Duplicate_Group'])
        self.assertEqual(results[0]['Total_in_Group'], 2)
        self.assertEqual(results[1]['Total_in_Group'], 2)
        # Hash should contain the filename for filename-based duplicate detection
        self.assertEqual(results[0]['Hash'], 'document.txt')
        self.assertEqual(results[1]['Hash'], 'document.txt')

    def test_get_duplicate_statistics(self):
        duplicates = {
            'document.txt': [
                {'Type': 'File', 'Name': 'document.txt', 'Path': '/path1', 'Extension': '.txt', 'File Name': 'document.txt', 'Size': 1024},
                {'Type': 'File', 'Name': 'document.txt', 'Path': '/path2', 'Extension': '.txt', 'File Name': 'document.txt', 'Size': 1024}
            ],
            'report.txt': [
                {'Type': 'File', 'Name': 'report.txt', 'Path': '/path3', 'Extension': '.txt', 'File Name': 'report.txt', 'Size': 2048},
                {'Type': 'File', 'Name': 'report.txt', 'Path': '/path4', 'Extension': '.txt', 'File Name': 'report.txt', 'Size': 2048},
                {'Type': 'File', 'Name': 'report.txt', 'Path': '/path5', 'Extension': '.txt', 'File Name': 'report.txt', 'Size': 2048}
            ]
        }
        
        total_files = get_duplicate_statistics(duplicates)
        
        # Check statistics - should return total count of duplicate files
        self.assertEqual(total_files, 5)  # 2 + 3 files


class TestDuplicateDetectorIntegration(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "subfolder"))
        
        # Create duplicate files with same filename in different locations
        with open(os.path.join(self.test_dir, "document.txt"), "w") as f:
            f.write("Original content")
        with open(os.path.join(self.test_dir, "subfolder", "document.txt"), "w") as f:
            f.write("Different content but same filename")
        
        # Create unique files
        with open(os.path.join(self.test_dir, "unique1.txt"), "w") as f:
            f.write("Unique content 1")
        with open(os.path.join(self.test_dir, "unique2.pdf"), "w") as f:
            f.write("Unique PDF content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_end_to_end_duplicate_detection(self):
        # Scan folder with files
        scan_results = collect_folders_and_files(self.test_dir, include_files=True)
        
        # Find duplicates
        duplicates = find_duplicates(scan_results)
        
        # Should find one group of duplicates
        self.assertEqual(len(duplicates), 1)
        
        # Format results
        formatted_results = format_duplicate_results(duplicates)
        self.assertEqual(len(formatted_results), 2)  # 2 duplicate files
        
        # Get statistics
        total_duplicate_files = get_duplicate_statistics(duplicates)
        self.assertEqual(total_duplicate_files, 2)  # 2 duplicate files in 1 group


if __name__ == "__main__":
    unittest.main()
