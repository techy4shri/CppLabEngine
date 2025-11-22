# Quick Start Guide

## First Time Setup

1. **Install Python 3.13+**
   - Download from python.org
   - Add to PATH during installation

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Compilers** (for production deployment)
   - Download MinGW-w64 32-bit and 64-bit
   - Extract to `compilers/mingw32` and `compilers/mingw64`
   - For graphics.h support, ensure libbgi libraries are in mingw32

4. **Run the IDE**
   ```bash
   python -m cpplab.main
   ```
   Or double-click `launch.bat`

## Creating Your First Project

### Console Application

1. Click **File → New Project**
2. Enter name: `HelloWorld`
3. Select location: `C:\Users\YourName\CppLabProjects`
4. Language: **C++**
5. Standard: **c++17**
6. Project Type: **Console Application**
7. Leave both checkboxes unchecked
8. Click **OK**

The IDE creates:
```cpp
#include <iostream>

int main() {
    std::cout << "Hello from CppLab!" << std::endl;
    return 0;
}
```

9. Press **F7** to build
10. Press **F5** to run

### Graphics Application

1. **File → New Project**
2. Name: `GraphicsDemo`
3. Project Type: **Graphics Application**
4. Click **OK**

Generated code:
```cpp
#include <graphics.h>
#include <iostream>

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

5. Build and run to see graphics window

### OpenMP Application

1. **File → New Project**
2. Name: `ParallelDemo`
3. Project Type: **Console Application**
4. Check **Enable OpenMP**
5. Click **OK**

Generated code:
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

## Keyboard Shortcuts

- **Ctrl+N**: New Project
- **Ctrl+O**: Open Project
- **Ctrl+S**: Save Current File
- **Ctrl+Shift+S**: Save All Files
- **F7**: Build Project
- **F5**: Run Executable
- **Ctrl+F5**: Build and Run

## Common Tasks

### Adding New Files

Currently, add files manually to project directory and update `.cpplab.json`:

```json
{
  "files": ["src/main.cpp", "src/helper.cpp"],
  "main_file": "src/main.cpp"
}
```

Then reload project in IDE.

### Changing Compiler Settings

Edit `.cpplab.json`:

```json
{
  "language": "cpp",
  "standard": "c++20",
  "features": {
    "graphics": false,
    "openmp": true
  }
}
```

Reload project for changes to take effect.

### Build Output

All compiler output appears in the output panel at the bottom:
- **Green text**: Success messages
- **Red text**: Error messages
- **Gray text**: Warnings

## Troubleshooting

### "Compiler not found"
- Ensure `compilers/mingw32` and `compilers/mingw64` directories exist
- Check that `bin/` subdirectories contain gcc.exe and g++.exe

### Graphics window doesn't appear
- Verify graphics.h libraries in `compilers/mingw32/lib/`
- Check that libbgi.a, libgdi32.a are present

### OpenMP doesn't work
- Ensure project is using 64-bit toolchain (graphics disabled)
- Check that `-fopenmp` appears in build command

### Build succeeds but run fails
- Check that toolchain bin directory is in PATH
- Verify DLLs are accessible

## Next Steps

- Explore DEVELOPMENT.md for architecture details
- Check README.md for complete feature list
- Experiment with different project types
