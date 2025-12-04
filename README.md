[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/techy4shri/CppLabEngine/total)
[![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/techy4shri)
<!--[![](https://img.shields.io/static/v1?label=Buy%20me%20a%20coffee&message=%E2%9D%A4&logo=buymeacoffee&color=%23fe8e86)](https://www.buymeacoffee.com/cpvalente)-->
# CppLabEngine 
A dedicated offline C/C++ IDE for college students with bundled MinGW compilers, graphics.h support, and OpenMP.
So I made this C/C++ IDE after being frustrated with Dev-Cpp (long live that software) and its inability to let me code in C++17/20 while working with omp.h and old graphics header. Now, this is by no means a proper alternative (in my unprofessional and inexperienced opinion) but, this works nicely, the app has extremely low build latency and runtime and most of all, it has support for both that legacy header and modern/shiny cpp which many students, including me learn.
Look, I know you would rather go with VS Code, but I ain't got that in my college lab and so this is my solution. Use it, critic it, support it, or ignore it, your choice. Have a nice day and happy programming :D

## Downloads

### Windows Release (Standalone .exe)

**Latest Release: v1.0.0**

📦 [Download latest release here!](https://github.com/techy4shri/CppLabEngine/releases)

**Quick Start:**
1. Download and extract the zip file anywhere on your computer
2. Run `CppLabEngine.exe` - no installation needed
3. Start coding with C/C++ immediately

**Requirements:** Windows 10/11 (64-bit) - native Windows only, Wine is NOT supported

### Linux/macOS Users

The Windows .exe build **does not work under Wine** due to Qt6 dependencies. Instead, run from source:

```bash
# Install dependencies
sudo apt install python3 python3-pip python3-venv mingw-w64  # Debian/Ubuntu
# or: brew install python3 mingw-w64  # macOS

# Clone and run
git clone https://github.com/techy4shri/CppLabEngine.git
cd CppLabEngine
python3 -m venv .venv
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
pip install -r requirements.txt
python run_cpplab.py
```

**Note:** MinGW cross-compilation toolchain is required on Linux/macOS to compile Windows executables.

## Features

- **Console and Graphics Projects**: Support for standard C/C++ and legacy graphics.h
- **Multiple C/C++ Standards**: C99/11/17/18/23, C++11/14/17/20/23 (toolchain-dependent)
- **Graphics Support**: Full graphics.h via 32-bit MinGW with WinBGIm library
- **OpenMP Support**: Parallel computing with 64-bit MinGW
- **Standalone File Mode**: Compile single .c/.cpp files without creating projects
- **Auto-Detection**: Automatically detects graphics.h and OpenMP pragmas in standalone files
- **Bundled Toolchains**: Includes MinGW 32-bit and 64-bit compilers
- **Portable**: No installation required, runs from any folder
- **Offline First**: Designed for use in college labs without internet

## Project Types

### Console Application
- Standard C/C++ console programs
- Optional graphics.h support (32-bit, OpenMP disabled)
- Optional OpenMP support (64-bit, graphics disabled)

### Graphics Application
- Dedicated graphics.h projects
- Always uses 32-bit toolchain
- OpenMP automatically disabled

## Architecture

### Directory Structure
```
CppLabEngine/
├── src/cpplab/
│   ├── main.py                 # Entry point
│   ├── app.py                  # Main window controller
│   ├── dialogs.py              # Project dialogs
│   ├── ui/
│   │   ├── MainWindow.ui
│   │   └── NewProjectDialog.ui
│   ├── widgets/
│   │   ├── code_editor.py      # Syntax-highlighted editor
│   │   ├── project_explorer.py # File tree
│   │   └── output_panel.py     # Build output
│   └── core/
│       ├── project_config.py   # Project data model
│       ├── toolchains.py       # Compiler configuration
│       ├── builder.py          # Build system
│       └── docs.py             # Documentation (future)
├── compilers/
│   ├── mingw32/                # 32-bit MinGW (for graphics.h)
│   └── mingw64/                # 64-bit MinGW (for OpenMP)
└── docs_source/                       # Offline documentation
```

### Toolchain Selection Rules

1. **Graphics Projects**: Always use 32-bit MinGW
   - `graphics=true` → `mingw32`
   - OpenMP automatically disabled

2. **Console Projects**:
   - `graphics=false` → `mingw64` (supports OpenMP)
   - `graphics=true` → `mingw32` (OpenMP forced off)

## Installation

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/techy4shri/CppLabEngine.git
   cd CppLabEngine
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add MinGW toolchains**:
   - Download MinGW 32-bit and 64-bit distributions
   - Extract to `compilers/mingw32` and `compilers/mingw64`
   - Ensure graphics.h libraries are in `mingw32/include` and `mingw32/lib`

4. **Run the IDE**:

   ```bash
   #The first command has issues so eh, use the .bat for now
   python -m cpplab.main
   ```
   Or use the launcher:
   ```bash
   launch.bat
   ```

### Building from Source

To create a standalone Windows distribution:

```bash
# Setup environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run build script
python tools/build_release.py
```

This will:
1. Clean previous builds
2. Run PyInstaller to create executable
3. Copy compilers/, examples/, and licenses/ into distribution
4. Create `dist/CppLabEngine-v0.1.0-win64.zip`

**Build Requirements:**
- Python 3.11+
- PyInstaller
- compilers/ directory with mingw32 and mingw64 toolchains (not in git)

See [BUILDING.md](BUILDING.md) for detailed build instructions.

## Usage

### Creating a New Project

1. **File → New Project**
2. Enter project name and location
3. Select language (C or C++) and standard
4. Choose project type:
   - **Console App**: Plain or with graphics/OpenMP
   - **Graphics App**: Dedicated graphics.h project
5. Click OK

### Building and Running

- **F7**: Build project
- **F5**: Run executable (must build first)
- **Ctrl+F5**: Build and run

### Project Configuration

Each project contains a `.cpplab.json` file:

```json
{
  "name": "MyProject",
  "path": "C:/Users/.../MyProject",
  "language": "cpp",
  "standard": "c++17",
  "project_type": "console",
  "features": {
    "graphics": false,
    "openmp": true
  },
  "files": ["src/main.cpp"],
  "main_file": "src/main.cpp"
}
```

## Known Limitations

This is an early release focused on core functionality:

- **Windows Only**: Currently targets Windows 10/11 (64-bit)
  - **Wine is NOT supported**: The PyInstaller .exe build requires native Windows for Qt6 dependencies
  - Linux/macOS users should run from source (see Downloads section)
- **No Debugger**: Integrated debugging not yet implemented (use GDB externally)
- **Build Performance**: Builds may be slow on some systems
  - Recommendation: Add CppLabEngine folder to antivirus exclusions for faster builds
- **Graphics + OpenMP**: Cannot use both features in same project (graphics requires 32-bit, OpenMP better on 64-bit)

## Code Style

The codebase follows these conventions:
- Minimal comments, clear naming preferred
- Short header comments for files and classes
- One-line comments inside functions where helpful
- No emojis or excessive commentary

## Future Enhancements

- [ ] Integrated debugger (GDB)
- [ ] Linux and macOS support (not in my agenda atm if I am being honest)
- [ ] Auto-completion
- [ ] Code templates library
- [ ] Project templates
- [x] Settings dialog for toolchain configuration
- [ ] Git integration (do we need this?)
- [ ] Enhanced documentation browser

## Requirements

**For End Users (Prebuilt):**
- Windows 10/11 (64-bit)

**For Development:**
- Python 3.13+
- PyQt6
- PyInstaller (for building)
- MinGW toolchains (not in repository)

## Troubleshooting

Having issues? Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common problems:
- Wine/Linux compatibility issues
- "Unknown Publisher" warnings
- Slow builds and antivirus interference
- Input/graphics/OpenMP problems
- And more...

## License

The source code of Cpp Lab Engine is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See the [LICENSE](LICENSE) file for full text.

This project also bundles third-party components under their own licenses, including (but not limited to):

- PyQt6 (GPL-3.0/commercial)
- MinGW-w64 / GCC toolchains (GPL/LGPL)

## Contributing

This project is designed for college lab environments. Contributions welcome for:
- Bug fixes
- Memory based optimizations
- Documentation improvements
- Additional project templates
- UI/UX enhancements
