# CppLab IDE v0.1.0 (Windows x64)

**First public release of CppLab IDE** - An offline C/C++ development environment designed for college students and educators.

---

## 🎉 Highlights

- **Offline-First Design**: Fully functional without internet access
- **Bundled Compilers**: Includes MinGW 32-bit and 64-bit toolchains
- **Graphics Support**: Full graphics.h library via WinBGIm (32-bit)
- **OpenMP Support**: Parallel computing with 64-bit compiler
- **Standalone Mode**: Compile single files without creating projects
- **Auto-Detection**: Automatically detects graphics.h and OpenMP usage
- **Portable**: No installation required, runs from any folder

## 📦 What's Included

- **CppLabIDE.exe** - Main IDE application (Windows GUI)
- **MinGW Compilers** - 32-bit (graphics) and 64-bit (OpenMP) toolchains
- **Example Projects** - Sample code for console, graphics, and OpenMP
- **Documentation** - Offline help and guides
- **License Files** - All component licenses included

## ✨ Features

### Project Management
- Console applications (C11, C++11/14/17/20)
- Graphics applications (graphics.h via WinBGIm)
- OpenMP parallel computing projects
- Project configuration via JSON files
- Recent projects list

### Code Editing
- Syntax highlighting for C/C++
- Line numbers
- File tree navigation
- Multiple file editing

### Build System
- Incremental builds (skip unchanged files)
- Syntax-only checking for fast error feedback
- Build profiling (optional)
- Toolchain and standard selection

### Keyboard Shortcuts
- **F5** - Build and Run
- **F7** - Build only
- **Ctrl+F5** - Build and Run (alternative)
- **Ctrl+S** - Save file
- **Ctrl+N** - New project

## 💾 Downloads

**File:** `CppLabIDE-v0.1.0-win64.zip`

**Size:** ~500-800 MB (includes compilers)

**SHA256:** (will be added after build)

## 🚀 Quick Start

1. **Download** the zip file from this release
2. **Extract** to any folder (e.g., `C:\CppLabIDE`)
3. **Run** `CppLabIDE.exe`
4. **Create** a new project or open a standalone .cpp file
5. **Build** with F7 or Build & Run with F5

No installation wizard. No admin rights needed after extraction.

## 📋 Requirements

- **OS:** Windows 10 or Windows 11 (64-bit)
- **Disk Space:** ~1.5 GB after extraction
- **RAM:** 2 GB minimum, 4 GB recommended
- **No additional software needed** - compilers are bundled

## ⚠️ Known Issues & Limitations

### Current Limitations
- **Windows only** - Linux and macOS support planned for future releases
- **No debugger** - Use external GDB for now (integrated debugger planned)
- **Build performance** - May be slow with active antivirus
  - **Solution:** Add CppLabIDE folder to antivirus exclusions
- **Graphics + OpenMP** - Cannot be used together in one project
  - Graphics requires 32-bit compiler
  - OpenMP works better with 64-bit compiler

### Workarounds
- For debugging: Use GDB from command line with compiled executables
- For faster builds: Exclude CppLabIDE folder in Windows Defender
- For both graphics and OpenMP: Create separate projects

## 📚 Documentation

### Included Guides
- Getting Started
- graphics.h Programming Guide
- OpenMP Programming Guide
- Project Configuration Reference
- Toolchain and Standard Selection

Access via **Help → Offline Documentation** in the IDE.

## 🐛 Reporting Issues

Found a bug or have a feature request?

**GitHub Issues:** https://github.com/techy4shri/CppLabEngine/issues

Please include:
- Windows version
- Steps to reproduce
- Error messages or screenshots
- Sample code if relevant

## 🔄 Upgrading from Previous Versions

This is the first release - no upgrade path needed!

## 📝 Changelog

See [CHANGELOG.md](https://github.com/techy4shri/CppLabEngine/blob/main/CHANGELOG.md) for full details.

## 🙏 Acknowledgments

- **MinGW-w64** - GCC compilers for Windows
- **WinBGIm** - Windows BGI graphics implementation
- **PyQt6** - Python Qt bindings
- **Python** - Programming language and ecosystem

## 📄 License

CppLabIDE is released under the MIT License (see included LICENSE file).

Bundled components have their own licenses (see `licenses/` folder):
- MinGW: GPL v3+ with runtime exception
- WinBGIm: BSD-style license
- PyQt6: GPL v3 / Commercial

---

**Enjoy coding with CppLab IDE!** 🚀

For support and updates, visit: https://github.com/techy4shri/CppLabEngine
