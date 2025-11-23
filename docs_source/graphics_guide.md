# Using graphics.h in CppLab IDE

## What is graphics.h?

`graphics.h` is a legacy graphics library originally developed by Borland for the BGI (Borland Graphics Interface) system. It provides simple 2D graphics functions for drawing shapes, lines, text, and managing a graphics window. This library is commonly used in:

- College computer graphics lab courses
- Legacy DOS-era C/C++ programs
- Educational projects requiring simple visualization

CppLab IDE includes a modern Windows port (WinBGIM) that allows `graphics.h` programs to run on contemporary Windows systems.

## When to Use graphics.h

**Good use cases:**
- Academic assignments requiring BGI-style graphics
- Quick prototyping of simple 2D visualizations
- Learning basic graphics programming concepts
- Porting legacy BGI code to Windows

**Not recommended for:**
- Modern production applications
- Complex graphics or game development (use SDL2, SFML, or OpenGL instead)
- Cross-platform projects (graphics.h is Windows-only in this IDE)

## Creating a Graphics Project

### Method 1: New Graphics App

1. Click **File > New > New Project** (or press `Ctrl+N`)
2. Enter your project name
3. Select **Graphics App** as the project type
4. Click **Create**

The IDE will:
- Automatically enable graphics.h support
- Switch to the 32-bit MinGW toolchain (required for WinBGIM)
- Generate a starter file with graphics initialization code

### Method 2: Enable Graphics in Console App

1. Create a **Console App** project
2. In the New Project dialog, check **"Enable graphics.h (32-bit, legacy)"**
3. Click **Create**

**Important:** Graphics projects always use the 32-bit (mingw32) toolchain, regardless of the toolchain dropdown selection. This is because WinBGIM libraries are compiled for 32-bit only.

## Basic Example Code

Here's a simple C++ program demonstrating graphics.h usage:

```cpp
#include <graphics.h>

int main() {
    // Initialize graphics
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    // Draw shapes
    setcolor(YELLOW);
    circle(320, 240, 100);
    
    rectangle(220, 140, 420, 340);
    
    line(220, 140, 420, 340);
    line(220, 340, 420, 140);
    
    // Draw text
    setcolor(WHITE);
    outtextxy(250, 450, (char*)"Press any key to exit...");
    
    // Wait for user input
    getch();
    
    // Clean up
    closegraph();
    return 0;
}
```

### Code Explanation

- **`initgraph(&gd, &gm, "")`**: Initializes the graphics system and creates a window
  - `gd = DETECT`: Auto-detect graphics driver
  - `gm`: Graphics mode (set automatically)
  - Third parameter: Path to BGI drivers (empty for default)

- **`setcolor(color)`**: Sets the current drawing color
  - Available colors: `BLACK`, `BLUE`, `GREEN`, `CYAN`, `RED`, `MAGENTA`, `BROWN`, `LIGHTGRAY`, `DARKGRAY`, `LIGHTBLUE`, `LIGHTGREEN`, `LIGHTCYAN`, `LIGHTRED`, `LIGHTMAGENTA`, `YELLOW`, `WHITE`

- **`getch()`**: Waits for a key press (keeps window open)

- **`closegraph()`**: Closes the graphics window and releases resources

## Coordinate System

- Origin (0, 0) is at the **top-left corner** of the window
- X increases to the right
- Y increases downward
- Default window size: 640×480 pixels

## Common Drawing Functions

### Lines and Shapes

```cpp
line(x1, y1, x2, y2);              // Draw line from (x1,y1) to (x2,y2)
circle(x, y, radius);               // Draw circle centered at (x,y)
rectangle(left, top, right, bottom); // Draw rectangle
ellipse(x, y, start, end, rx, ry);  // Draw ellipse arc
arc(x, y, start, end, radius);      // Draw circular arc
```

### Filled Shapes

```cpp
setfillstyle(SOLID_FILL, color);    // Set fill pattern and color
bar(left, top, right, bottom);      // Draw filled rectangle
fillellipse(x, y, rx, ry);          // Draw filled ellipse
floodfill(x, y, border_color);      // Flood fill from point (x,y)
```

### Text

```cpp
outtextxy(x, y, (char*)"text");     // Draw text at (x,y)
settextstyle(font, direction, size); // Set font properties
```

### Styling

```cpp
setcolor(color);                    // Set drawing color
setbkcolor(color);                  // Set background color
setlinestyle(style, pattern, thickness); // Set line style
```

## Limitations

1. **32-bit Only**: Graphics projects require the 32-bit MinGW toolchain. You cannot use 64-bit compilation.

2. **Legacy API**: The API design is from the 1990s and lacks modern features like:
   - Hardware acceleration
   - Anti-aliasing
   - True color support (limited to 16 colors in many functions)
   - Event-driven input handling

3. **Single Window**: Only one graphics window can be active at a time.

4. **Basic Rendering**: No support for:
   - Image formats (PNG, JPG, etc.)
   - 3D graphics
   - Sprites or animations (requires manual implementation)

5. **Windows Only**: This implementation only works on Windows.

## Troubleshooting

### No Window Appears

**Symptom:** Program runs but no graphics window opens.

**Solutions:**
1. Ensure `initgraph()` is called before any drawing functions
2. Check that you're calling `getch()` or `delay()` to keep the window open
3. Verify the project type is set to "Graphics App" or graphics is enabled

### Linking Errors

**Symptom:** Build fails with errors like "undefined reference to `initgraph`"

**Solutions:**
1. Verify project type is **Graphics App** or graphics feature is enabled
2. Check that the IDE is using the mingw32 (32-bit) toolchain
3. Ensure WinBGIM libraries are present in `toolchains/mingw32/lib/`

### String Literal Warnings

**Symptom:** Compiler warnings about ISO C++ forbidding string literal conversion.

**Solution:** Cast string literals to `(char*)`:
```cpp
// Correct:
outtextxy(100, 100, (char*)"Hello");

// Causes warning:
outtextxy(100, 100, "Hello");
```

### Runtime Error: "Graphics not initialized"

**Symptom:** Program crashes with graphics initialization error.

**Solutions:**
1. Ensure `initgraph()` completed successfully
2. Check return value: `int err = graphresult(); if (err != grOk) { /* handle error */ }`
3. Verify BGI drivers are accessible

## Further Resources

- **WinBGIM Documentation**: [winbgim.codecutter.org](http://winbgim.codecutter.org/)
- **Original BGI Reference**: Available in legacy Borland C++ documentation
- **Tutorial Series**: Search for "graphics.h tutorial" for numerous examples

## Migration Path

If you outgrow graphics.h limitations, consider migrating to:

- **SDL2**: Simple DirectMedia Layer, modern cross-platform multimedia
- **SFML**: Simple and Fast Multimedia Library, C++ focused
- **raylib**: Beginner-friendly game development library
- **OpenGL**: Industry-standard 3D graphics API

CppLab IDE may support these libraries in future versions.
