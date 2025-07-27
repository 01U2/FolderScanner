import unittest
import tempfile
import os
import shutil
import pandas as pd
from pathlib import Path

from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure
from src.file_io import save_to_excel
from src.duplicate_detector import calculate_file_hash, find_duplicates, format_duplicate_results, get_duplicate_statistics


class TestFolderScanner(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "subfolder"))
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(self.test_dir, "file2.pdf"), "w") as f:
            f.write("PDF content")
        with open(os.path.join(self.test_dir, "subfolder", "file3.docx"), "w") as f:
            f.write("DOCX content")

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


class TestFolderReplicator(unittest.TestCase):

    def setUp(self):
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.source_dir, "subfolder"))
        with open(os.path.join(self.source_dir, "file1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(self.source_dir, "subfolder", "file2.pdf"), "w") as f:
            f.write("PDF content")

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
        # Create test files with known content
        self.file1_path = os.path.join(self.test_dir, "file1.txt")
        self.file2_path = os.path.join(self.test_dir, "file2.txt")
        self.duplicate_path = os.path.join(self.test_dir, "duplicate.txt")
        self.unique_path = os.path.join(self.test_dir, "unique.txt")
        
        # Create files with same content (duplicates)
        with open(self.file1_path, "w") as f:
            f.write("Hello World")
        with open(self.duplicate_path, "w") as f:
            f.write("Hello World")
            
        # Create files with different content
        with open(self.file2_path, "w") as f:
            f.write("Different content")
        with open(self.unique_path, "w") as f:
            f.write("Unique content here")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_calculate_file_hash(self):
        hash1 = calculate_file_hash(self.file1_path)
        hash2 = calculate_file_hash(self.duplicate_path)
        hash3 = calculate_file_hash(self.file2_path)
        
        # Same content should produce same hash
        self.assertEqual(hash1, hash2)
        # Different content should produce different hash
        self.assertNotEqual(hash1, hash3)
        # Hash should be a non-empty string
        self.assertIsInstance(hash1, str)
        self.assertGreater(len(hash1), 0)

    def test_calculate_file_hash_sha256(self):
        hash_md5 = calculate_file_hash(self.file1_path, 'md5')
        hash_sha256 = calculate_file_hash(self.file1_path, 'sha256')
        
        # Different algorithms should produce different hashes
        self.assertNotEqual(hash_md5, hash_sha256)
        # SHA256 hash should be longer than MD5
        self.assertGreater(len(hash_sha256), len(hash_md5))

    def test_calculate_file_hash_nonexistent_file(self):
        result = calculate_file_hash("/nonexistent/file.txt")
        self.assertIsNone(result)

    def test_find_duplicates(self):
        # Create file list similar to scanner output
        file_list = [
            {'Type': 'File', 'Name': 'file1.txt', 'Path': self.file1_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'duplicate.txt', 'Path': self.duplicate_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'file2.txt', 'Path': self.file2_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'unique.txt', 'Path': self.unique_path, 'Extension': '.txt'},
            {'Type': 'Folder', 'Name': 'somefolder', 'Path': '/some/path', 'Extension': ''}
        ]
        
        duplicates = find_duplicates(file_list)
        
        # Should find one group of duplicates
        self.assertEqual(len(duplicates), 1)
        
        # Each duplicate group should have exactly 2 files
        for hash_val, files in duplicates.items():
            self.assertEqual(len(files), 2)
            # Check that both files have the same hash
            self.assertEqual(files[0]['Hash'], files[1]['Hash'])
            # Check that files have Size information
            self.assertIn('Size', files[0])
            self.assertIn('Size', files[1])

    def test_find_duplicates_no_duplicates(self):
        # Create file list with unique files only
        file_list = [
            {'Type': 'File', 'Name': 'file2.txt', 'Path': self.file2_path, 'Extension': '.txt'},
            {'Type': 'File', 'Name': 'unique.txt', 'Path': self.unique_path, 'Extension': '.txt'}
        ]
        
        duplicates = find_duplicates(file_list)
        
        # Should find no duplicates
        self.assertEqual(len(duplicates), 0)

    def test_format_duplicate_results(self):
        # Create a sample duplicate detection result
        duplicates = {
            'hash123': [
                {'Type': 'File', 'Name': 'file1.txt', 'Path': '/path1', 'Extension': '.txt', 'Hash': 'hash123', 'Size': 100},
                {'Type': 'File', 'Name': 'file2.txt', 'Path': '/path2', 'Extension': '.txt', 'Hash': 'hash123', 'Size': 100}
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

    def test_get_duplicate_statistics(self):
        duplicates = {
            'hash123': [
                {'Type': 'File', 'Name': 'file1.txt', 'Path': '/path1', 'Extension': '.txt', 'Hash': 'hash123', 'Size': 1024},
                {'Type': 'File', 'Name': 'file2.txt', 'Path': '/path2', 'Extension': '.txt', 'Hash': 'hash123', 'Size': 1024}
            ],
            'hash456': [
                {'Type': 'File', 'Name': 'file3.txt', 'Path': '/path3', 'Extension': '.txt', 'Hash': 'hash456', 'Size': 2048},
                {'Type': 'File', 'Name': 'file4.txt', 'Path': '/path4', 'Extension': '.txt', 'Hash': 'hash456', 'Size': 2048},
                {'Type': 'File', 'Name': 'file5.txt', 'Path': '/path5', 'Extension': '.txt', 'Hash': 'hash456', 'Size': 2048}
            ]
        }
        
        stats = get_duplicate_statistics(duplicates)
        
        # Check statistics
        self.assertEqual(stats['total_duplicate_files'], 5)  # 2 + 3 files
        self.assertEqual(stats['total_groups'], 2)
        # Wasted space: (1 extra copy of 1024) + (2 extra copies of 2048) = 1024 + 4096 = 5120 bytes
        self.assertEqual(stats['total_wasted_space_bytes'], 5120)
        self.assertEqual(stats['total_wasted_space_mb'], 0.00)  # Small files, rounds to 0


class TestDuplicateDetectorIntegration(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "subfolder"))
        
        # Create duplicate files in different locations
        with open(os.path.join(self.test_dir, "original.txt"), "w") as f:
            f.write("This is duplicate content")
        with open(os.path.join(self.test_dir, "subfolder", "copy.txt"), "w") as f:
            f.write("This is duplicate content")
        
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
        stats = get_duplicate_statistics(duplicates)
        self.assertEqual(stats['total_duplicate_files'], 2)
        self.assertEqual(stats['total_groups'], 1)
        self.assertGreater(stats['total_wasted_space_bytes'], 0)


if __name__ == "__main__":
    unittest.main()
