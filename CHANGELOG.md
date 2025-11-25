# Changelog

All notable changes to CppLabEngine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-11-26

### Major Release - Production Ready

First stable production release of CppLabEngine with comprehensive improvements, bug fixes, and polish.

### Added

**Diagnostics & Error Handling:**
- Advanced compiler error/warning/note parsing with line-level detail
- Problems panel with severity-based color coding (errors: red, warnings: yellow, notes: blue)
- Double-click navigation from Problems panel to exact error location in source
- In-editor error line highlighting with colored backgrounds
- Status bar error/warning/note counts after each build
- Support for GCC/MinGW fatal error messages

**UI Enhancements:**
- Application rebranded to "CppLabEngine" with custom logo
- About dialog with GitHub wiki link
- Removed output/console tabs in favor of external terminal for console apps
- Improved build status messages with elapsed time
- Window icon and application identity properly set

**Build & Run Improvements:**
- Standalone single-file executables now placed next to source file (not in build/)
- Console applications launch in external Windows terminal for better I/O interaction
- Graphics and OpenMP programs run detached (non-blocking)
- Fixed executable path detection for single-file vs. project builds
- C17 set as default C standard (was previously inconsistent)

**Code Quality:**
- All import statements moved to top of files across the codebase
- Added comprehensive unit tests for project explorer path resolution
- Fixed ProjectExplorer bug using wrong attribute (`path` vs `root_path`)
- Type safety improvements and code organization

**Documentation:**
- GitHub wiki integration in Help menu
- Updated About dialog with project information

### Fixed

- **Critical**: Fixed TypeError in `get_executable_path()` when checking Path objects
- **Critical**: Fixed ProjectExplorer emitting relative paths instead of absolute paths
- Build directory creation now only happens for multi-file projects
- Standalone file detection now correctly handles Path vs string types
- Test suite compatibility issues resolved (34 tests passing)

### Changed

- **Breaking**: Removed in-app console output panel (console apps use external terminal)
- Default C standard changed from C11 to C17 for new single-file projects
- Build results now focus on diagnostics rather than raw compiler output
- Error highlighting persists until next build (cleared automatically)

### Technical Improvements

- Refactored diagnostics into dedicated `core/diagnostics.py` module
- Dataclass-based Diagnostic representation with severity levels
- Regex-based GCC output parsing supporting multiple message formats
- Qt ExtraSelections for efficient error highlighting
- Improved separation of concerns between build, diagnostics, and UI

### Known Issues

None

### Release Assets

- Portable Windows distribution (~454 MB)
- Bundled MinGW 32-bit and 64-bit compilers
- Complete documentation and examples included

---

## [0.1.0] - 2025-11-24

### Initial Release

First public release of CppLabEngine - an offline C/C++ development environment for Windows.

### Added

**Core Features:**
- Project-based workflow with Console and Graphics project types
- Standalone file mode for quick .c/.cpp compilation without projects
- Syntax-highlighted code editor with line numbers
- Project explorer with file tree navigation
- Build output panel with error/warning display
- Toolchain selector (MinGW 32-bit / 64-bit)
- C/C++ standard selector (C99/11/17/18/23, C++11/14/17/20/23)

**Graphics Support:**
- Full graphics.h library support via WinBGIm
- Automatic 32-bit MinGW selection for graphics projects
- Sample graphics projects included

**OpenMP Support:**
- Parallel computing with OpenMP pragmas
- 64-bit MinGW for optimal performance
- Sample OpenMP projects included

**Build System:**
- Incremental builds (skips unchanged files)
- Syntax-only checking for fast error feedback
- Build profiling (opt-in via environment variable)
- Auto-detection of graphics.h and OpenMP in standalone files

**User Experience:**
- Keyboard shortcuts (F5: Build & Run, F7: Build, Ctrl+S: Save)
- Recent projects list
- Offline documentation (Help menu)
- About dialog with version information

**Bundled Components:**
- MinGW-w64 64-bit compiler (for console and OpenMP)
- MinGW 32-bit compiler (for graphics.h)
- WinBGIm graphics library
- Example projects (hello_cpp17, hello_openmp, hello_graphics)
- Offline documentation

### Known Issues

- Windows only (no Linux/macOS support yet)
- No integrated debugger
- Build performance may be slow with antivirus active
- Cannot use graphics and OpenMP in same project
- No code completion or IntelliSense yet

### Technical Details

- Built with Python 3.13 and PyQt6
- Packaged with PyInstaller (onedir mode)
- Portable distribution (no installation required)
- Total size: ~500-800 MB (includes compilers)

---

## Future Versions

See [README.md](README.md) for planned enhancements.
