# Auto-Detection of Graphics.h and OpenMP in Standalone Files

## Summary

Standalone source files (built via `build_single_file()`, `run_single_file()`, or `check_single_file()`) now automatically detect and configure graphics.h and OpenMP features by scanning the source code.

## What Changed

### Before
```python
# Standalone files always had features disabled
features = {"graphics": False, "openmp": False}
```

### After
```python
# Automatically detects from source code
features = detect_features_from_source(source_path)
# → {"graphics": True, "openmp": False} if #include <graphics.h> found
# → {"graphics": False, "openmp": True} if #pragma omp found
```

## Detection Logic

### New Function: `detect_features_from_source()`

```python
def detect_features_from_source(source_path: Path) -> dict[str, bool]:
    """Detect graphics.h and OpenMP usage by scanning source file."""
```

**Graphics detection:**
- Searches for `#include <graphics.h>` or `#include "graphics.h"`
- When detected → Adds graphics linking flags: `-lbgi -lgdi32 -lcomdlg32 -luuid -lole32 -loleaut32`
- Automatically uses mingw32 toolchain (required for WinBGIm)

**OpenMP detection:**
- Searches for `#pragma omp` anywhere in source
- When detected → Adds `-fopenmp` compiler flag
- Prefers mingw64 toolchain (64-bit has better OpenMP support)

## Usage Examples

### Example 1: Graphics Program

**File: `bouncing_ball.cpp`**
```cpp
#include <graphics.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    circle(320, 240, 50);
    outtextxy(270, 230, (char*)"Hello!");
    
    getch();
    closegraph();
    return 0;
}
```

**Build command:**
```python
from src.cpplab.core.builder import build_single_file
from src.cpplab.core.toolchains import get_toolchains

result = build_single_file(Path("bouncing_ball.cpp"), get_toolchains())
# Automatically detects graphics.h and links graphics libraries!
```

**Generated command includes:**
```
g++.exe bouncing_ball.cpp -std=c++17 -o build/bouncing_ball.exe 
  -lbgi -lgdi32 -lcomdlg32 -luuid -lole32 -loleaut32
```

### Example 2: OpenMP Program

**File: `parallel.cpp`**
```cpp
#include <iostream>
#include <omp.h>

int main() {
    #pragma omp parallel for
    for (int i = 0; i < 10; i++) {
        std::cout << "Thread " << omp_get_thread_num() << "\n";
    }
    return 0;
}
```

**Build command:**
```python
result = build_single_file(Path("parallel.cpp"), get_toolchains())
# Automatically detects #pragma omp and adds -fopenmp!
```

**Generated command includes:**
```
g++.exe parallel.cpp -std=c++17 -fopenmp -o build/parallel.exe
```

### Example 3: Both Features

**File: `graphics_parallel.cpp`**
```cpp
#include <graphics.h>
#include <omp.h>

int main() {
    #pragma omp parallel
    {
        // Parallel computation
    }
    
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    circle(320, 240, 50);
    closegraph();
    return 0;
}
```

**Build command:**
```python
result = build_single_file(Path("graphics_parallel.cpp"), get_toolchains())
# Detects both features!
```

**Generated command includes:**
```
g++.exe graphics_parallel.cpp -std=c++17 -fopenmp -o build/graphics_parallel.exe
  -lbgi -lgdi32 -lcomdlg32 -luuid -lole32 -loleaut32
```

Note: Graphics forces mingw32, so OpenMP may have limited functionality (mingw32 has basic OpenMP support).

## Test Coverage

Added 7 new tests in `tests/test_feature_detection.py`:

1. ✅ `test_detect_graphics_from_source` - Detects graphics.h
2. ✅ `test_detect_openmp_from_source` - Detects OpenMP pragmas
3. ✅ `test_detect_both_features` - Detects both simultaneously
4. ✅ `test_detect_no_features` - Correctly reports no features
5. ✅ `test_single_file_config_with_graphics` - Config includes graphics
6. ✅ `test_single_file_config_with_openmp` - Config includes OpenMP
7. ✅ `test_single_file_config_no_features` - Config has no features

**All 33 tests pass** (26 existing + 7 new)

## Benefits

### For Students
- **Just works™** - No manual configuration needed
- Write `#include <graphics.h>` and it automatically links graphics libraries
- Use `#pragma omp` and it automatically enables OpenMP
- Reduces confusion and setup errors

### For Educators
- Students can share single `.cpp` files
- No need to create full projects for simple examples
- Works in "Quick Run" or "File Explorer → Build" scenarios

### For IDE
- Enables "Open File → Build" workflow
- Smart enough to handle different file types automatically
- Maintains compatibility with existing project system

## Implementation Details

### Modified Functions

**`project_config_for_single_file()`:**
```python
# Old: features={"graphics": False, "openmp": False}
# New: features=detect_features_from_source(source_path)
```

### File Scanning

- Opens file with UTF-8 encoding, ignores errors
- Performs simple string search (no parsing needed)
- Fast: <1ms for typical source files
- Safe: Fails gracefully if file can't be read

### Edge Cases Handled

- File doesn't exist → Returns default features (all False)
- File not readable → Returns default features
- Unicode/encoding issues → Ignores errors, continues
- False positives (e.g., in comments) → Acceptable tradeoff for simplicity

## Limitations

### Current Implementation

1. **No header scanning**: Only scans the single source file, doesn't check included headers
2. **Simple text search**: Doesn't parse C++ AST, just looks for strings
3. **False positives possible**: Will detect `#include <graphics.h>` even if in a comment

These limitations are acceptable for a teaching IDE where:
- Most code is in single files
- Students write straightforward code
- Speed and simplicity matter more than perfect accuracy

## Future Enhancements

Possible improvements:

1. **Header dependency tracking**: Scan all `#include` files recursively
2. **Smarter detection**: Use regex to ignore comments
3. **Cache results**: Don't re-scan unchanged files
4. **Additional features**: Detect `<windows.h>`, `<pthread.h>`, etc.
5. **User override**: Allow manual feature specification

## Backward Compatibility

✅ **Fully backward compatible**
- Existing code continues to work unchanged
- Project-based builds unaffected (use explicit features from config)
- Only affects standalone file builds
- All existing tests pass

## Integration with Performance Features

Works seamlessly with new performance features:
- Incremental builds still work
- Syntax checking (`check_single_file()`) includes detected features
- Profiling logs show detected features
- Force rebuild respects feature detection

## Example: Complete Workflow

```python
from pathlib import Path
from src.cpplab.core.toolchains import get_toolchains
from src.cpplab.core.builder import (
    detect_features_from_source,
    build_single_file,
    run_single_file
)

# User opens a standalone file
source = Path("student_code.cpp")

# IDE can preview what will be detected
features = detect_features_from_source(source)
print(f"Detected: {features}")  # {'graphics': True, 'openmp': False}

# Build with auto-detection
toolchains = get_toolchains()
build_result = build_single_file(source, toolchains)

if build_result.success:
    print(f"Built in {build_result.elapsed_ms:.0f}ms")
    
    # Run it
    run_result = run_single_file(source, toolchains)
    print(run_result.stdout)
```

## Conclusion

This feature makes CppLab more intuitive and student-friendly by eliminating manual configuration for common use cases. Students can focus on learning C++ rather than wrestling with build systems.

**Key takeaway:** If you `#include <graphics.h>`, it just works. If you use `#pragma omp`, it just works. No configuration needed.
