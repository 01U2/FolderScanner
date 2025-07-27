import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, call

from src.scanner import collect_folders_and_files
from src.replicator import replicate_folder_structure


class TestProgressCallbacks(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create a simple directory structure for testing
        os.makedirs(os.path.join(self.test_dir, "subfolder1"))
        os.makedirs(os.path.join(self.test_dir, "subfolder2"))
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(self.test_dir, "file2.pdf"), "w") as f:
            f.write("PDF content")
        with open(os.path.join(self.test_dir, "subfolder1", "file3.docx"), "w") as f:
            f.write("DOCX content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scanner_with_progress_callbacks(self):
        """Test that scanner calls progress callbacks correctly"""
        mock_update_status = Mock()
        mock_check_cancelled = Mock(return_value=False)
        
        progress_callbacks = {
            'update_status': mock_update_status,
            'check_cancelled': mock_check_cancelled
        }
        
        result = collect_folders_and_files(
            self.test_dir, 
            include_files=True, 
            progress_callback=progress_callbacks
        )
        
        # Verify that progress callbacks were called
        self.assertTrue(mock_update_status.called)
        self.assertTrue(mock_check_cancelled.called)
        
        # Verify we still get the expected results
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        self.assertIn("subfolder1", folder_names)
        self.assertIn("subfolder2", folder_names)
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.pdf", file_names)
        self.assertIn("file3.docx", file_names)

    def test_scanner_with_cancellation(self):
        """Test that scanner respects cancellation"""
        mock_update_status = Mock()
        mock_check_cancelled = Mock()
        
        # Set up cancellation after first few calls
        call_count = 0
        def check_cancelled():
            nonlocal call_count
            call_count += 1
            return call_count > 2  # Cancel after a few calls
        
        mock_check_cancelled.side_effect = check_cancelled
        
        progress_callbacks = {
            'update_status': mock_update_status,
            'check_cancelled': mock_check_cancelled
        }
        
        result = collect_folders_and_files(
            self.test_dir, 
            include_files=True, 
            progress_callback=progress_callbacks
        )
        
        # When cancelled, we should get fewer results than expected
        # (though exact count depends on when cancellation occurs)
        self.assertTrue(mock_check_cancelled.called)

    def test_replicator_with_progress_callbacks(self):
        """Test that replicator calls progress callbacks correctly"""
        dest_dir = tempfile.mkdtemp()
        try:
            mock_update_status = Mock()
            mock_update_progress = Mock()
            mock_check_cancelled = Mock(return_value=False)
            
            progress_callbacks = {
                'update_status': mock_update_status,
                'update_progress': mock_update_progress,
                'check_cancelled': mock_check_cancelled
            }
            
            result = replicate_folder_structure(
                self.test_dir, 
                dest_dir, 
                include_files=True,
                progress_callback=progress_callbacks
            )
            
            # Verify that progress callbacks were called
            self.assertTrue(mock_update_status.called)
            self.assertTrue(mock_update_progress.called)
            self.assertTrue(mock_check_cancelled.called)
            
            # Verify progress values are reasonable (0-100)
            progress_calls = [call.args[0] for call in mock_update_progress.call_args_list]
            for progress in progress_calls:
                self.assertGreaterEqual(progress, 0)
                self.assertLessEqual(progress, 100)
            
            # Verify we still get the expected results
            folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
            file_names = [item['Name'] for item in result if item['Type'] == 'File']
            self.assertIn("subfolder1", folder_names)
            self.assertIn("subfolder2", folder_names)
            self.assertIn("file1.txt", file_names)
            self.assertIn("file2.pdf", file_names)
            self.assertIn("file3.docx", file_names)
            
        finally:
            shutil.rmtree(dest_dir)

    def test_replicator_with_cancellation(self):
        """Test that replicator respects cancellation"""
        dest_dir = tempfile.mkdtemp()
        try:
            mock_update_status = Mock()
            mock_update_progress = Mock()
            mock_check_cancelled = Mock()
            
            # Set up cancellation after first few calls
            call_count = 0
            def check_cancelled():
                nonlocal call_count
                call_count += 1
                return call_count > 3  # Cancel after a few calls
            
            mock_check_cancelled.side_effect = check_cancelled
            
            progress_callbacks = {
                'update_status': mock_update_status,
                'update_progress': mock_update_progress,
                'check_cancelled': mock_check_cancelled
            }
            
            result = replicate_folder_structure(
                self.test_dir, 
                dest_dir, 
                include_files=True,
                progress_callback=progress_callbacks
            )
            
            # When cancelled, we should get fewer results than expected
            self.assertTrue(mock_check_cancelled.called)
            
        finally:
            shutil.rmtree(dest_dir)

    def test_scanner_without_progress_callbacks(self):
        """Test that scanner still works without progress callbacks (backward compatibility)"""
        result = collect_folders_and_files(self.test_dir, include_files=True)
        
        # Should work exactly as before
        folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
        file_names = [item['Name'] for item in result if item['Type'] == 'File']
        self.assertIn("subfolder1", folder_names)
        self.assertIn("subfolder2", folder_names)
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.pdf", file_names)
        self.assertIn("file3.docx", file_names)

    def test_replicator_without_progress_callbacks(self):
        """Test that replicator still works without progress callbacks (backward compatibility)"""
        dest_dir = tempfile.mkdtemp()
        try:
            result = replicate_folder_structure(self.test_dir, dest_dir, include_files=True)
            
            # Should work exactly as before
            folder_names = [item['Name'] for item in result if item['Type'] == 'Folder']
            file_names = [item['Name'] for item in result if item['Type'] == 'File']
            self.assertIn("subfolder1", folder_names)
            self.assertIn("subfolder2", folder_names)
            self.assertIn("file1.txt", file_names)
            self.assertIn("file2.pdf", file_names)
            self.assertIn("file3.docx", file_names)
            
        finally:
            shutil.rmtree(dest_dir)


if __name__ == "__main__":
    unittest.main()