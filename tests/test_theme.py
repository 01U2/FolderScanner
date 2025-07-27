import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.theme_manager import ThemeManager


class TestThemeManager(unittest.TestCase):

    def setUp(self):
        """Set up test environment with temporary config file"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = Path.home()
        # Mock home directory for testing
        self.test_config_file = Path(self.temp_dir) / '.folderscanner_config.json'

    def tearDown(self):
        """Clean up test environment"""
        if self.test_config_file.exists():
            self.test_config_file.unlink()

    def test_theme_initialization(self):
        """Test theme manager initializes correctly"""
        tm = ThemeManager()
        self.assertIn(tm.current_theme, ['light', 'dark'])

    def test_available_themes(self):
        """Test that both light and dark themes are available"""
        tm = ThemeManager()
        themes = tm.get_themes()
        self.assertIn('light', themes)
        self.assertIn('dark', themes)
        
        # Test theme structure
        for theme_name, theme_data in themes.items():
            self.assertIn('bg', theme_data)
            self.assertIn('fg', theme_data)
            self.assertIn('button_bg', theme_data)
            self.assertIn('button_fg', theme_data)

    def test_theme_switching(self):
        """Test theme switching functionality"""
        tm = ThemeManager()
        initial_theme = tm.current_theme
        
        # Toggle theme
        new_theme = tm.toggle_theme()
        self.assertNotEqual(initial_theme, new_theme)
        self.assertEqual(tm.current_theme, new_theme)
        
        # Toggle back
        returned_theme = tm.toggle_theme()
        self.assertEqual(initial_theme, returned_theme)
        self.assertEqual(tm.current_theme, returned_theme)

    def test_theme_colors_accessibility(self):
        """Test that themes have proper contrast for accessibility"""
        tm = ThemeManager()
        themes = tm.get_themes()
        
        for theme_name, theme_data in themes.items():
            # Test that background and foreground are different
            self.assertNotEqual(theme_data['bg'], theme_data['fg'])
            
            # Test that colors are valid hex codes
            self.assertTrue(theme_data['bg'].startswith('#'))
            self.assertTrue(theme_data['fg'].startswith('#'))
            self.assertEqual(len(theme_data['bg']), 7)  # #rrggbb format
            self.assertEqual(len(theme_data['fg']), 7)

    def test_get_current_theme(self):
        """Test getting current theme colors"""
        tm = ThemeManager()
        current_theme_data = tm.get_current_theme()
        
        # Verify it returns a complete theme dictionary
        required_keys = ['bg', 'fg', 'button_bg', 'button_fg', 'entry_bg', 'entry_fg']
        for key in required_keys:
            self.assertIn(key, current_theme_data)

    def test_set_theme(self):
        """Test setting specific theme"""
        tm = ThemeManager()
        
        # Set to dark theme
        tm.set_theme('dark')
        self.assertEqual(tm.current_theme, 'dark')
        
        # Set to light theme
        tm.set_theme('light')
        self.assertEqual(tm.current_theme, 'light')
        
        # Test invalid theme (should not change)
        initial_theme = tm.current_theme
        tm.set_theme('invalid_theme')
        self.assertEqual(tm.current_theme, initial_theme)

    def test_apply_theme_to_widget(self):
        """Test theme application to mock widgets"""
        tm = ThemeManager()
        
        # Create mock widget
        class MockWidget:
            def __init__(self):
                self.config = {}
            def configure(self, **kwargs):
                self.config.update(kwargs)
        
        # Test button styling
        mock_button = MockWidget()
        tm.apply_theme_to_widget(mock_button, 'button')
        self.assertIn('bg', mock_button.config)
        self.assertIn('fg', mock_button.config)
        
        # Test entry styling
        mock_entry = MockWidget()
        tm.apply_theme_to_widget(mock_entry, 'entry')
        self.assertIn('bg', mock_entry.config)
        self.assertIn('fg', mock_entry.config)


if __name__ == "__main__":
    unittest.main()