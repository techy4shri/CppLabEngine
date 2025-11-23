# CppLab IDE - Quick Reference Card

## Launch Commands

```bash
# Development mode
python -m cpplab.main

# Or use launcher
launch.bat

# Pre-flight check
python test_setup.py
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Project |
| `Ctrl+O` | Open Project |
| `Ctrl+S` | Save Current File |
| `Ctrl+Shift+S` | Save All Files |
| `F7` | Build Project |
| `F5` | Run Executable |
| `Ctrl+F5` | Build and Run |

## Project Structure

```
MyProject/
├── .cpplab.json       # Project configuration
├── src/
│   └── main.cpp       # Source files
└── build/
    └── MyProject.exe  # Compiled output
```

## Project Configuration (.cpplab.json)

```json
{
  "name": "ProjectName",
  "path": "C:/path/to/project",
  "language": "cpp",          // "c" or "cpp"
  "standard": "c++17",        // "c++20", "c++17", "c++14", "c11", etc.
  "project_type": "console",  // "console" or "graphics"
  "features": {
    "graphics": false,        // Enable graphics.h (32-bit)
    "openmp": true            // Enable OpenMP (64-bit only)
  },
  "files": ["src/main.cpp"],
  "main_file": "src/main.cpp"
}
```

## Toolchain Selection Rules

| Project Type | Graphics | OpenMP | Toolchain |
|--------------|----------|--------|-----------|
| Console      | ❌       | ✅     | mingw64   |
| Console      | ❌       | ❌     | mingw64   |
| Console      | ✅       | ❌     | mingw32   |
| Graphics     | ✅       | ❌     | mingw32   |

**Key Rules**:
- Graphics → Always 32-bit
- Graphics + OpenMP → Not allowed (OpenMP forced off)
- No Graphics → 64-bit with optional OpenMP

## Build Flags

### All Projects
- C: `gcc -std=<standard>`
- C++: `g++ -std=<standard>`

### With OpenMP
- Add: `-fopenmp`
- Only on mingw64

### With Graphics
- Add: `-I<include> -L<lib> -lbgi -lgdi32 -lcomdlg32 -luuid -loleaut32 -lole32`
- Only on mingw32

## Directory Layout

```
CppLabEngine/
├── src/cpplab/              # Source code
│   ├── main.py              # Entry point
│   ├── app.py               # Main window
│   ├── dialogs.py           # Dialogs
│   ├── ui/                  # Qt Designer files
│   ├── widgets/             # Custom widgets
│   └── core/                # Business logic
│       ├── project_config.py
│       ├── toolchains.py
│       ├── builder.py
│       └── docs.py
│
├── compilers/               # MinGW toolchains (add these)
│   ├── mingw32/
│   └── mingw64/
│
└── docs/                    # Offline docs (future)
```

## Build & Package

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_setup.py

# Build distribution
build.bat

# Or manually with PyInstaller
pyinstaller cpplab.spec
```

## Code Templates

### Console (Plain)
```cpp
#include <iostream>

int main() {
    std::cout << "Hello from CppLab!" << std::endl;
    return 0;
}
```

### Graphics
```cpp
#include <graphics.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");
    
    outtextxy(250, 200, "Hello from CppLab!");
    circle(300, 250, 50);
    
    getch();
    closegraph();
    return 0;
}
```

### OpenMP
```cpp
#include <iostream>
#include <omp.h>

int main() {
    std::cout << "Hello from CppLab!" << std::endl;
    
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        #pragma omp critical
        std::cout << "Thread " << tid << " says hi!" << std::endl;
    }
    
    return 0;
}
```

## Common Issues

### Issue: "Compiler not found"
**Solution**: Add MinGW to `compilers/mingw32` and `compilers/mingw64`

### Issue: Graphics window doesn't appear
**Solution**: Ensure graphics libraries in `mingw32/lib/`
- libbgi.a
- libgdi32.a
- Others listed in build flags

### Issue: OpenMP doesn't work
**Solution**: 
- Disable graphics (use 64-bit toolchain)
- Check `-fopenmp` in build output

### Issue: "Module not found" error
**Solution**: Run from project root or use `launch.bat`

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `QUICKSTART.md` | Getting started |
| `DEVELOPMENT.md` | Architecture & design |
| `CONTRIBUTING.md` | How to contribute |
| `TODO.md` | Roadmap |
| `IMPLEMENTATION_SUMMARY.md` | What's implemented |

## Module Dependencies

```
main.py
└── app.py (MainWindow)
    ├── dialogs.py (NewProjectDialog)
    ├── widgets/
    │   ├── code_editor.py
    │   ├── project_explorer.py
    │   └── output_panel.py
    └── core/
        ├── project_config.py
        ├── toolchains.py
        └── builder.py
```

## Quick Tips

1. **Always save before building** (Ctrl+Shift+S)
2. **Check build output** for errors
3. **Use F5 after building** to run
4. **PATH includes toolchain bin** for DLLs
5. **Graphics requires 32-bit**, OpenMP uses 64-bit
6. **Can't mix graphics and OpenMP** (hardware limitation)

## Learning Resources

- C++ Reference: https://cppreference.com (online)
- Graphics.h: Legacy Borland Graphics Interface
- OpenMP: https://openmp.org (online)

## Support

- GitHub Issues: Bug reports & features
- GitHub Discussions: Questions & help

---

**Version**: 1.0  
**Updated**: 2025-11-23  
**License**: See LICENSE file
