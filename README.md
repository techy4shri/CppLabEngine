# CppLab IDE

A dedicated C/C++ IDE for college students with support for old and new libraries and modules alike like graphics.h and OpenMP.

## Features

- **Modern IDE Interface**: Clean, intuitive PyQt6-based GUI with syntax highlighting
- **Graphics Support**: Full support for legacy graphics.h library (32-bit)
- **OpenMP Support**: Multi-threading support for modern C++ applications (64-bit)
- **Portable Toolchains**: Bundled MinGW compilers (32-bit and 64-bit)
- **Project Management**: Simple project configuration with JSON-based settings
- **Offline First**: Designed for offline use in college labs

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
└── docs/                       # Offline documentation (future)
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
   python -m cpplab.main
   ```
   Or use the launcher:
   ```bash
   launch.bat
   ```

### Production Packaging

Use PyInstaller to create a standalone executable:

```bash
pyinstaller --name CppLabIDE --windowed --add-data "src/cpplab/ui;ui" --add-data "compilers;compilers" src/cpplab/main.py
```

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

## Code Style

The codebase follows these conventions:
- Minimal comments, clear naming preferred
- Short header comments for files and classes
- One-line comments inside functions where helpful
- No emojis or excessive commentary

## Future Enhancements

- [ ] Offline documentation browser
- [ ] Code templates library
- [ ] Integrated debugger (GDB)
- [ ] Project templates
- [ ] Settings dialog for project configuration
- [ ] Auto-completion and IntelliSense
- [ ] Git integration

## Requirements

- Python 3.13+
- PyQt6
- Windows (tested on Windows 10/11)
- MinGW toolchains (bundled in production)

## License

See LICENSE file for details.

## Contributing

This project is designed for college lab environments. Contributions welcome for:
- Bug fixes
- Documentation improvements
- Additional project templates
- UI/UX enhancements