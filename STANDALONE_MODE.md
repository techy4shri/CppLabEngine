# Standalone Source File Mode

## Overview

CppLab IDE now supports two workflows:

1. **Project Mode** (existing) - Full project with `.cpplab.json`, multiple files, project configuration
2. **Standalone Mode** (new) - Quick compile single `.c` or `.cpp` files without creating a project

## Usage

### Opening a Standalone File

**Menu:** File → Open Source File... (Ctrl+Shift+O)

1. Click "File → Open Source File..." or press `Ctrl+Shift+O`
2. Select a `.c` or `.cpp` file from the file dialog
3. The file opens in the editor
4. Status bar shows: `Standalone: <filename>`
5. Build/Run buttons become available

### Building Standalone Files

**Menu:** Build → Build Project (F7) or toolbar button

- Saves the file automatically
- Detects language from extension (`.c` → C, `.cpp`/`.cc`/`.cxx` → C++)
- Uses default standards:
  - C: `c11`
  - C++: `c++17`
- Creates `build/` directory in the same folder as your source file
- Compiles using mingw64 (64-bit, console mode only)
- Output executable: `<file_dir>/build/<filename>.exe`

**Build Output:**
```
=== Build Started ===

Command: D:\...\mingw64\bin\g++.exe myfile.cpp -std=c++17 -o myfile.exe

=== Build Succeeded ===
```

### Running Standalone Files

**Menu:** Build → Run Project (F5) or toolbar button

- Checks if executable exists (prompts to build if not)
- Runs the executable in a new console window
- Shows exit code in build output

**Menu:** Build → Build and Run (Ctrl+F5) or toolbar button

- Builds the file
- If build succeeds, automatically runs the executable

### Standalone vs Project Mode

| Feature | Project Mode | Standalone Mode |
|---------|-------------|-----------------|
| **Setup** | Create project with dialog | Just open a file |
| **Configuration** | `.cpplab.json` in project root | No config file |
| **Multiple Files** | ✓ Yes, all files in project | ✗ Single file only |
| **Project Explorer** | ✓ Shows file tree | ✗ Empty |
| **Graphics.h** | ✓ Available (32-bit) | ✗ Not in v1.1 |
| **OpenMP** | ✓ Available (64-bit) | ✗ Not in v1.1 |
| **Build Output** | `<project>/build/<name>.exe` | `<file_dir>/build/<name>.exe` |
| **Toolchain** | Auto-selected (32/64-bit) | Always mingw64 |
| **Clean Build** | ✓ Build → Clean | ✗ N/A |

## Examples

### Example 1: Simple Hello World

1. Create `hello.cpp`:
```cpp
#include <iostream>

int main() {
    std::cout << "Hello from CppLab!" << std::endl;
    return 0;
}
```

2. File → Open Source File... → Select `hello.cpp`
3. Press F7 to build
4. Press F5 to run
5. See output in console window

### Example 2: C Program

1. Create `test.c`:
```c
#include <stdio.h>

int main() {
    printf("Testing standalone C compilation\n");
    return 0;
}
```

2. File → Open Source File... → Select `test.c`
3. Build → Build and Run (Ctrl+F5)
4. Executable created at: `test\build\test.exe`

## Technical Details

### Auto-Detection

- **Language:** Determined from file extension
  - `.c` → C language, standard = `c11`
  - `.cpp`, `.cc`, `.cxx` → C++ language, standard = `c++17`

### Synthetic ProjectConfig

Internally, standalone files create a temporary `ProjectConfig`:
```python
ProjectConfig(
    name=source_path.stem,           # filename without extension
    root_path=source_path.parent,    # file's directory
    language="c" or "cpp",           # auto-detected
    standard="c11" or "c++17",       # defaults
    project_type="console",          # always console
    features={"graphics": False, "openmp": False},
    files=[source_path.name],        # single file
    main_file=source_path.name       # this file
)
```

### Build Command

For `example.cpp` in `D:\code\`:
```
mingw64\bin\g++.exe D:\code\example.cpp -std=c++17 -o D:\code\build\example.exe
```

### Limitations in v1.1

- ✗ No graphics.h support (use project mode)
- ✗ No OpenMP support (use project mode)
- ✗ Single file only (can't link multiple files)
- ✗ No custom compiler flags
- ✗ Always uses default standards

## Switching Between Modes

### Standalone → Project

If you start with a standalone file and want project features:

1. File → New Project
2. Select project type (Console/Graphics)
3. Copy your code to the new project's `main.cpp`
4. Close the standalone file tab

### Project → Standalone

If you want to quickly test a single file:

1. File → Open Source File...
2. Select any `.c`/`.cpp` file
3. Build and run independently of any project

**Note:** Opening a standalone file while a project is open will clear the project context. The IDE switches to standalone mode.

## When to Use Each Mode

### Use Standalone Mode When:
- ✓ Learning C/C++ basics
- ✓ Quick tests and experiments
- ✓ Single-file programs
- ✓ Code snippets and examples
- ✓ Fast prototyping
- ✓ No need for project organization

### Use Project Mode When:
- ✓ Multiple source files
- ✓ Need graphics.h support
- ✓ Need OpenMP support
- ✓ Want project organization
- ✓ Larger programs
- ✓ Need custom build settings

## UI Indicators

**Status Bar:**
- Project Mode: `Project: MyProject`
- Standalone Mode: `Standalone: hello.cpp`
- No file: `No project`

**Window Title:**
- Project Mode: `CppLab IDE - MyProject`
- Standalone Mode: `CppLab IDE - hello.cpp`

**Project Explorer:**
- Project Mode: Shows file tree
- Standalone Mode: Empty

**Build Menu:**
- Both modes: All actions enabled (Build, Run, Build & Run)
- Clean: Only enabled in project mode

## Troubleshooting

### "No Source File to build"
- Make sure you have a `.c` or `.cpp` file open in the editor
- The current tab must be a code file, not empty

### "Unsupported file extension"
- Only `.c`, `.cpp`, `.cc`, `.cxx` files are supported
- Check your file extension

### Build fails with "command not found"
- Ensure MinGW toolchains are installed in `compilers/mingw64`
- Check toolchain availability warning on startup

### Can't find executable
- Check if `build/` directory was created in your source file's folder
- Build first before running (F7, then F5)

### Want graphics.h or OpenMP
- Use project mode instead: File → New Project
- Select appropriate project type and features
