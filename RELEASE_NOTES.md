# 📦 Release Notes – FolderScanner v2.1.0

**Release Date:** 2025-08-10

## 🚀 New Features

- **Filename-Based Duplicate Detection:** Added duplicate file detection that identifies files with identical filenames across different locations in the scanned directory structure.
- **Smart UI Controls:** "Detect Duplicates" checkbox now only appears when "Include Files" is enabled, creating a more intuitive user experience.
- **Cross-Platform File Paths:** Improved file path handling to work correctly across different operating systems (Windows, macOS, Linux).
- **Enhanced Threading:** Background task processing with daemon threads for better application responsiveness.

## 🛠️ Improvements

- **UI Layout Enhancements:** 
  - Increased window height to 600x500 for better content visibility
  - Improved checkbox text ("Exclude Folder(s) in the scan")
  - Dynamic showing/hiding of duplicate detection controls
- **File I/O Improvements:**
  - Automatic detection of user's Documents/Desktop folder for saving reports
  - Cross-platform compatible save location logic with fallbacks
  - Removed hardcoded C:\temp dependency
- **Code Quality:**
  - Simplified duplicate detection logic from hash-based to filename-based approach
  - Better error handling and user feedback
  - Improved threading implementation with proper daemon threads
  - Enhanced parameter passing in scanning functions

## 🔧 Technical Changes

- **Duplicate Detection Method:** Changed from content-based hashing (MD5/SHA256) to filename-based detection for faster processing
- **Statistics Simplification:** Streamlined duplicate statistics to focus on file count rather than complex space calculations
- **Test Suite Updates:** Updated all test cases to work with filename-based duplicate detection approach
- **Workspace Configuration:** Added VS Code workspace settings and Python environment configuration

## 📝 Notes

- **Breaking Change:** Duplicate detection now works by comparing filenames instead of file content hashes
- Files with the same name in different directories will be detected as duplicates regardless of their content
- Please report any issues or feature requests via the [GitHub Issues page](https://github.com/01U2/FolderScanner/issues).
- See the README for updated usage instructions.

---

# 📦 Release Notes – FolderScanner v2.0.0

**Release Date:** 2025-07-27

## 🚀 New Features

- **Files Scanning:** Scans folder contents to include files as an optional selection.
- **Files Filter:** Files filter options enabled.
## 🛠️ Improvements

- Initial implementation with robust error handling and user instructions.

## 📝 Notes

- Please report any issues or feature requests via the [GitHub Issues page](https://github.com/your-username/your-repo/issues).
- See the README for usage instructions.


# 📦 Release Notes – FolderScanner v1.0.0

**Release Date:** 2025-07-09

## 🚀 New Features

- **Folder Scanning:** Scan any folder and its subfolders to collect detailed structure information (name, path, parent, depth).
- **Export to Excel:** Export the scanned folder structure to an Excel file for easy analysis.
- **Structure Replication:** Optionally replicate the scanned folder structure to a new location, creating empty folders that mirror the original hierarchy.
- **User-Friendly GUI:** Simple graphical interface for selecting folders, exporting data, and managing options.
- **Error Handling:** Clear error messages and user feedback throughout the process.

## 🛠️ Improvements

- Initial implementation with robust error handling and user instructions.

## 📝 Notes

- Please report any issues or feature requests via the [GitHub Issues page](https://github.com/your-username/your-repo/issues).
- See the README for usage instructions.

