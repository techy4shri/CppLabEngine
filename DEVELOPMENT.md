# Development Guide

## Project Overview

CppLab IDE is a Windows-based offline C/C++ IDE designed for college labs, with special support for legacy graphics.h and modern OpenMP.

## Architecture

### Core Components

1. **project_config.py**: Data model for projects
   - `ProjectConfig`: Main data class with load/save
   - `create_new_project()`: Project initialization
   - Template generation for different project types

2. **toolchains.py**: Compiler management
   - `ToolchainConfig`: Toolchain metadata
   - `select_toolchain()`: Rule-based toolchain selection
   - Hardcoded paths relative to app directory

3. **builder.py**: Build system
   - `build_project()`: Compile sources with appropriate flags
   - `run_project()`: Execute built executable
   - `BuildResult`: Build output container

4. **app.py**: Main window controller
   - Qt UI integration
   - Menu action handlers
   - Editor tab management
   - Build thread coordination

### Widget Components

- **CodeEditor**: Syntax-highlighted text editor
- **ProjectExplorer**: File tree navigation
- **OutputPanel**: Build messages display

### Dialog Components

- **NewProjectDialog**: Project creation wizard
  - Dynamic UI based on project type
  - Graphics/OpenMP mutual exclusion
  - Language-specific standard options

## Design Decisions

### Why Two Toolchains?

- **graphics.h**: Only available in 32-bit MinGW builds
- **OpenMP**: Better support in 64-bit builds
- Cannot mix due to ABI incompatibilities

### Project Type Logic

```
if project_type == "graphics":
    graphics = true
    openmp = false
    toolchain = mingw32

elif project_type == "console":
    if graphics == true:
        openmp = false
        toolchain = mingw32
    else:
        toolchain = mingw64
        # OpenMP allowed
```

### Build Process

1. User triggers build (F7)
2. Save all open files
3. Select appropriate toolchain
4. Generate compiler command:
   - Compiler: gcc (C) or g++ (C++)
   - Standard: -std=<standard>
   - OpenMP: -fopenmp (if enabled)
   - Graphics: -lbgi -lgdi32 etc. (if enabled)
5. Execute in background thread
6. Capture stdout/stderr
7. Display in output panel

### File Organization

```
Project/
├── .cpplab.json       # Project metadata
├── src/
│   └── main.cpp       # Source files
└── build/
    └── Project.exe    # Compiled output
```

## Adding Features

### New Project Template

Edit `_generate_main_template()` in `project_config.py`:

```python
if language == "cpp" and some_feature:
    return """#include <some_header.h>
    
int main() {
    // Your template
    return 0;
}
"""
```

### New Build Flag

Edit `_build_compiler_command()` in `builder.py`:

```python
if project_config.features.some_feature:
    cmd.append("-some-flag")
```

### New Dialog

1. Create `.ui` file in `ui/`
2. Load with `uic.loadUi()` in dialog class
3. Connect signals in `_connect_signals()`
4. Extract data in getter method

## Testing Workflow

### Manual Testing

1. **Create Console Project**:
   - Verify 64-bit toolchain used
   - Test OpenMP build
   - Run and verify output

2. **Create Graphics Project**:
   - Verify 32-bit toolchain used
   - Test graphics.h compilation
   - Run and verify window appears

3. **Create Console + Graphics**:
   - Verify 32-bit toolchain used
   - Verify OpenMP disabled
   - Test graphics code compiles

### Common Issues

**Issue**: Build fails with "compiler not found"
- **Solution**: Check `compilers/mingw32` and `compilers/mingw64` exist
- **Solution**: Verify PATH in subprocess call

**Issue**: Graphics program crashes on run
- **Solution**: Ensure graphics DLLs in toolchain bin directory
- **Solution**: Verify PATH includes toolchain bin in `run_project()`

**Issue**: UI file not loading
- **Solution**: Check path calculation in dialog constructors
- **Solution**: Verify .ui files in `src/cpplab/ui/`

## Packaging for Distribution

### PyInstaller Configuration

Create `cpplab.spec`:

```python
a = Analysis(
    ['src/cpplab/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/cpplab/ui/*.ui', 'ui'),
        ('compilers/mingw32', 'compilers/mingw32'),
        ('compilers/mingw64', 'compilers/mingw64'),
    ],
    hiddenimports=['PyQt6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CppLabIDE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CppLabIDE'
)
```

Build:
```bash
pyinstaller cpplab.spec
```

### Distribution Structure

```
CppLabIDE/
├── CppLabIDE.exe
├── compilers/
│   ├── mingw32/
│   └── mingw64/
└── docs/ (optional)
```

## Code Style Guidelines

### Comments

```python
# File-level: Short description of module purpose

class SomeClass:
    # Class-level: What this class does
    
    def some_method(self):
        # Inside: Only where helpful
        x = compute()  # Brief inline note
```

### Naming

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Private methods: `_snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Imports

```python
# Standard library
import os
import sys

# Third-party
from PyQt6.QtWidgets import QWidget

# Local
from .core import module
```

## Future Improvements

### Priority 1
- [ ] Settings dialog for project configuration
- [ ] Multiple file support in projects
- [ ] File → Add File action

### Priority 2
- [ ] GDB integration for debugging
- [ ] Project templates (SDL, OpenGL, etc.)
- [ ] Code snippets library

### Priority 3
- [ ] Auto-completion (QScintilla)
- [ ] Find/replace
- [ ] Git integration

### Priority 4
- [ ] Plugin system
- [ ] Theme customization
- [ ] Offline documentation browser
