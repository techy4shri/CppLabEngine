# Changelog

All notable changes to CppLab IDE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2025-11-24

### Initial Release

First public release of CppLab IDE - an offline C/C++ development environment for Windows.

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
