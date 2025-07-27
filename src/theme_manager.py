"""
Theme management system for FolderScanner application.
Provides light and dark themes with proper accessibility contrast.
"""

import json
import os
from pathlib import Path

class ThemeManager:
    def __init__(self):
        self.config_file = Path.home() / '.folderscanner_config.json'
        self.current_theme = 'light'
        self.load_config()
        
    def get_themes(self):
        """Define light and dark themes with accessibility-compliant colors."""
        return {
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'button_bg': '#e1e1e1',
                'button_fg': '#000000',
                'button_active_bg': '#d4d4d4',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'frame_bg': '#f0f0f0',
                'accent': '#0078d4',
                'accent_light': '#106ebe',
                'success': '#107c10',
                'warning': '#ff8c00',
                'error': '#d13438'
            },
            'dark': {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'button_active_bg': '#505050',
                'entry_bg': '#404040',
                'entry_fg': '#ffffff',
                'frame_bg': '#353535',
                'accent': '#0078d4',
                'accent_light': '#4cc2ff',
                'success': '#6bb700',
                'warning': '#ffb900',
                'error': '#ff6b6b'
            }
        }
    
    def get_current_theme(self):
        """Get the current theme colors."""
        themes = self.get_themes()
        return themes.get(self.current_theme, themes['light'])
    
    def set_theme(self, theme_name):
        """Set the current theme and save to config."""
        if theme_name in self.get_themes():
            self.current_theme = theme_name
            self.save_config()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.set_theme(new_theme)
        return new_theme
    
    def load_config(self):
        """Load theme preference from config file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', 'light')
        except (json.JSONDecodeError, IOError):
            self.current_theme = 'light'
    
    def save_config(self):
        """Save theme preference to config file."""
        try:
            config = {'theme': self.current_theme}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except IOError:
            pass  # Fail silently if can't save config
    
    def apply_theme_to_widget(self, widget, widget_type='default'):
        """Apply current theme colors to a tkinter widget."""
        theme = self.get_current_theme()
        
        try:
            if widget_type == 'button':
                widget.configure(
                    bg=theme['button_bg'],
                    fg=theme['button_fg'],
                    activebackground=theme['button_active_bg'],
                    activeforeground=theme['button_fg']
                )
            elif widget_type == 'entry':
                widget.configure(
                    bg=theme['entry_bg'],
                    fg=theme['entry_fg'],
                    insertbackground=theme['fg']
                )
            elif widget_type == 'frame':
                widget.configure(bg=theme['frame_bg'])
            elif widget_type == 'label':
                widget.configure(
                    bg=theme['bg'],
                    fg=theme['fg']
                )
            elif widget_type == 'checkbutton':
                widget.configure(
                    bg=theme['bg'],
                    fg=theme['fg'],
                    selectcolor=theme['entry_bg'],
                    activebackground=theme['bg'],
                    activeforeground=theme['fg']
                )
            elif widget_type == 'root':
                widget.configure(bg=theme['bg'])
            else:
                # Default styling
                widget.configure(
                    bg=theme['bg'],
                    fg=theme['fg']
                )
        except Exception:
            pass  # Some widgets might not support all options