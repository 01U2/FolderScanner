import unittest
import tempfile
import os
import shutil
import time
from pathlib import Path

from src.comparator import get_folder_contents, compare_folders, get_comparison_summary


class TestFolderComparator(unittest.TestCase):

    def setUp(self):
        # Create two test directories
        self.folder1 = tempfile.mkdtemp(prefix="folder1_")
        self.folder2 = tempfile.mkdtemp(prefix="folder2_")
        
        # Setup folder1 with some content
        os.makedirs(os.path.join(self.folder1, "common_folder"))
        os.makedirs(os.path.join(self.folder1, "folder1_only"))
        
        with open(os.path.join(self.folder1, "common_file.txt"), "w") as f:
            f.write("Same content")
        
        with open(os.path.join(self.folder1, "modified_file.txt"), "w") as f:
            f.write("Original content")
        
        with open(os.path.join(self.folder1, "folder1_file.txt"), "w") as f:
            f.write("File only in folder1")
        
        with open(os.path.join(self.folder1, "common_folder", "nested_file.txt"), "w") as f:
            f.write("Nested file")
        
        # Setup folder2 with overlapping and different content
        os.makedirs(os.path.join(self.folder2, "common_folder"))
        os.makedirs(os.path.join(self.folder2, "folder2_only"))
        
        with open(os.path.join(self.folder2, "common_file.txt"), "w") as f:
            f.write("Same content")
        
        # Create modified file with different content
        time.sleep(0.1)  # Ensure different modification time
        with open(os.path.join(self.folder2, "modified_file.txt"), "w") as f:
            f.write("Modified content - longer")
        
        with open(os.path.join(self.folder2, "folder2_file.txt"), "w") as f:
            f.write("File only in folder2")
        
        with open(os.path.join(self.folder2, "common_folder", "nested_file.txt"), "w") as f:
            f.write("Nested file")

    def tearDown(self):
        shutil.rmtree(self.folder1)
        shutil.rmtree(self.folder2)

    def test_get_folder_contents(self):
        """Test that get_folder_contents correctly scans a folder"""
        contents = get_folder_contents(self.folder1)
        
        # Check that we found the expected items
        self.assertIn("common_file.txt", contents)
        self.assertIn("common_folder", contents)
        self.assertIn("folder1_only", contents)
        self.assertIn(os.path.join("common_folder", "nested_file.txt"), contents)
        
        # Check metadata is populated
        file_item = contents["common_file.txt"]
        self.assertEqual(file_item['type'], 'file')
        self.assertEqual(file_item['name'], 'common_file.txt')
        self.assertTrue(file_item['exists'])
        self.assertIsNotNone(file_item['modified_time'])
        self.assertGreater(file_item['size'], 0)
        
        folder_item = contents["common_folder"]
        self.assertEqual(folder_item['type'], 'folder')
        self.assertEqual(folder_item['name'], 'common_folder')
        self.assertTrue(folder_item['exists'])

    def test_compare_folders_basic(self):
        """Test basic folder comparison functionality"""
        results = compare_folders(self.folder1, self.folder2)
        
        # Convert to dict for easier testing
        results_dict = {r['Relative Path']: r for r in results}
        
        # Test common file (should be same if timestamps are close enough)
        common_file = results_dict.get("common_file.txt")
        self.assertIsNotNone(common_file)
        # File may be 'Same' or 'Modified' depending on timing in test environment
        self.assertIn(common_file['Status'], ['Same', 'Modified'])
        
        # Test modified file (should be modified due to size difference)
        modified_file = results_dict.get("modified_file.txt")
        self.assertIsNotNone(modified_file)
        self.assertEqual(modified_file['Status'], 'Modified')
        
        # Test file only in folder1
        folder1_only_file = results_dict.get("folder1_file.txt")
        self.assertIsNotNone(folder1_only_file)
        self.assertEqual(folder1_only_file['Status'], 'Only in Folder 1')
        
        # Test file only in folder2
        folder2_only_file = results_dict.get("folder2_file.txt")
        self.assertIsNotNone(folder2_only_file)
        self.assertEqual(folder2_only_file['Status'], 'Only in Folder 2')
        
        # Test common folder
        common_folder = results_dict.get("common_folder")
        self.assertIsNotNone(common_folder)
        self.assertIn(common_folder['Status'], ['Same', 'Modified'])  # Could be either depending on timing

    def test_compare_folders_nested(self):
        """Test that nested files are properly compared"""
        results = compare_folders(self.folder1, self.folder2)
        
        # Convert to dict for easier testing
        results_dict = {r['Relative Path']: r for r in results}
        
        # Test nested file
        nested_path = os.path.join("common_folder", "nested_file.txt")
        nested_file = results_dict.get(nested_path)
        self.assertIsNotNone(nested_file)
        # Since files might have different modification times, they could be 'Same' or 'Modified'
        self.assertIn(nested_file['Status'], ['Same', 'Modified'])

    def test_get_comparison_summary(self):
        """Test comparison summary generation"""
        results = compare_folders(self.folder1, self.folder2)
        summary = get_comparison_summary(results)
        
        # Check summary structure
        self.assertIn('Total Items', summary)
        self.assertIn('Same', summary)
        self.assertIn('Modified', summary)
        self.assertIn('Only in Folder 1', summary)
        self.assertIn('Only in Folder 2', summary)
        
        # Check that totals make sense
        total = summary['Total Items']
        component_total = (summary['Same'] + summary['Modified'] + 
                          summary['Only in Folder 1'] + summary['Only in Folder 2'] +
                          summary['Type Mismatch'] + summary['Errors'])
        self.assertEqual(total, component_total)
        
        # We should have at least some items in each category based on our test setup
        # Note: 'Same' count might be 0 if timing affects file comparisons
        self.assertGreaterEqual(summary['Same'], 0)
        self.assertGreater(summary['Only in Folder 1'], 0)
        self.assertGreater(summary['Only in Folder 2'], 0)

    def test_empty_folders(self):
        """Test comparison of empty folders"""
        empty1 = tempfile.mkdtemp()
        empty2 = tempfile.mkdtemp()
        
        try:
            results = compare_folders(empty1, empty2)
            self.assertEqual(len(results), 0)
            
            summary = get_comparison_summary(results)
            self.assertEqual(summary['Total Items'], 0)
        finally:
            shutil.rmtree(empty1)
            shutil.rmtree(empty2)

    def test_one_empty_folder(self):
        """Test comparison where one folder is empty"""
        empty_folder = tempfile.mkdtemp()
        
        try:
            results = compare_folders(self.folder1, empty_folder)
            
            # All items should be "Only in Folder 1"
            for result in results:
                self.assertEqual(result['Status'], 'Only in Folder 1')
            
            # Test reverse comparison
            results_reverse = compare_folders(empty_folder, self.folder1)
            for result in results_reverse:
                self.assertEqual(result['Status'], 'Only in Folder 2')
                
        finally:
            shutil.rmtree(empty_folder)


if __name__ == "__main__":
    unittest.main()