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
// Basic line drawing
line(x1, y1, x2, y2);              // Draw line from (x1,y1) to (x2,y2)

// Circles and arcs
circle(x, y, radius);               // Draw circle centered at (x,y)
arc(x, y, start_angle, end_angle, radius);  // Draw circular arc (angles in degrees, 0° = 3 o'clock)

// Rectangles
rectangle(left, top, right, bottom); // Draw rectangle outline

// Ellipses
ellipse(x, y, start_angle, end_angle, rx, ry);  // Draw ellipse arc with x-radius rx and y-radius ry

// Polygons
drawpoly(num_points, points);       // Draw polygon from array of points
// Example: int points[] = {100,100, 200,150, 150,200, 100,100}; drawpoly(4, points);

// Curved lines
moveto(x, y);                       // Move current position (without drawing)
lineto(x, y);                       // Draw line from current position to (x,y)
linerel(dx, dy);                    // Draw line relative to current position

// Pixel operations
putpixel(x, y, color);              // Set pixel at (x,y) to color
int c = getpixel(x, y);             // Get color of pixel at (x,y)
```

### Filled Shapes

```cpp
// Set fill pattern and color
setfillstyle(pattern, color);       // Set fill pattern
// Patterns: EMPTY_FILL, SOLID_FILL, LINE_FILL, LTSLASH_FILL, SLASH_FILL,
//           BKSLASH_FILL, LTBKSLASH_FILL, HATCH_FILL, XHATCH_FILL, INTERLEAVE_FILL

// Filled shapes
bar(left, top, right, bottom);      // Draw filled rectangle (no border)
bar3d(left, top, right, bottom, depth, topflag);  // Draw 3D bar
fillellipse(x, y, rx, ry);          // Draw filled ellipse
fillpoly(num_points, points);       // Draw filled polygon
pieslice(x, y, start_angle, end_angle, radius);  // Draw filled pie slice
sector(x, y, start_angle, end_angle, rx, ry);    // Draw filled elliptical sector

// Flood fill
floodfill(x, y, border_color);      // Fill area starting at (x,y) until border_color
setfillpattern(pattern, color);     // Set custom fill pattern (8x8 bytes)
```

### Text Functions

```cpp
// Basic text output
outtextxy(x, y, (char*)"text");     // Draw text at (x,y)
outtext((char*)"text");              // Draw text at current position

// Text settings
settextstyle(font, direction, charsize);
// Fonts: DEFAULT_FONT, TRIPLEX_FONT, SMALL_FONT, SANS_SERIF_FONT, GOTHIC_FONT
// Direction: HORIZ_DIR (0) or VERT_DIR (1)
// Size: 1-10 for default font, pixel height for others

settextjustify(horiz, vert);        // Set text alignment
// Horizontal: LEFT_TEXT, CENTER_TEXT, RIGHT_TEXT
// Vertical: BOTTOM_TEXT, CENTER_TEXT, TOP_TEXT

setusercharsize(multx, divx, multy, divy);  // Set custom character size scaling

// Text measurements
int w = textwidth((char*)"text");   // Get width of text string in pixels
int h = textheight((char*)"text");  // Get height of text string in pixels
```

### Color and Style Functions

```cpp
// Color control
setcolor(color);                    // Set drawing (foreground) color
setbkcolor(color);                  // Set background color
setpalette(index, color);           // Change palette entry

// Standard colors (0-15)
// BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, BROWN, LIGHTGRAY,
// DARKGRAY, LIGHTBLUE, LIGHTGREEN, LIGHTCYAN, LIGHTRED, LIGHTMAGENTA, YELLOW, WHITE

// RGB colors (if supported)
int color = COLOR(r, g, b);         // Create RGB color (r,g,b: 0-255)
setrgbpalette(index, r, g, b);      // Set palette entry to RGB

// Line styles
setlinestyle(linestyle, pattern, thickness);
// Styles: SOLID_LINE, DOTTED_LINE, CENTER_LINE, DASHED_LINE, USERBIT_LINE
// Thickness: NORM_WIDTH (1 pixel) or THICK_WIDTH (3 pixels)

// Write modes
setwritemode(mode);                 // Set logical drawing mode
// Modes: COPY_PUT (replace), XOR_PUT (XOR), OR_PUT, AND_PUT, NOT_PUT
```

### Screen and Window Functions

```cpp
// Screen info
int x = getmaxx();                  // Get maximum X coordinate
int y = getmaxy();                  // Get maximum Y coordinate
int cx = getx();                    // Get current X position
int cy = gety();                    // Get current Y position

// Viewport (clipping region)
setviewport(left, top, right, bottom, clip);  // Set active viewport
// clip: 1 = clip drawing to viewport, 0 = no clipping
clearviewport();                    // Clear current viewport

// Screen manipulation
cleardevice();                      // Clear entire screen to background color
setactivepage(page);                // Set active page for drawing
setvisualpage(page);                // Set visible page (for double buffering)

// Image functions
void* img = malloc(imagesize(left, top, right, bottom));  // Allocate image buffer
getimage(left, top, right, bottom, img);  // Save screen region to buffer
putimage(x, y, img, mode);          // Draw image at (x,y) with mode
// Modes: COPY_PUT, XOR_PUT, OR_PUT, AND_PUT, NOT_PUT
```

### Input Functions

```cpp
// Keyboard input
int ch = getch();                   // Wait for and return key press (no echo)
int kbhit();                        // Check if key was pressed (non-blocking)

// Mouse input (WinBGIM extensions)
void registermousehandler(int event, void (*handler)(int, int));
// Events: WM_LBUTTONDOWN, WM_RBUTTONDOWN, WM_MOUSEMOVE, etc.

int mousex();                       // Get current mouse X coordinate
int mousey();                       // Get current mouse Y coordinate
int ismouseclick(int button);       // Check if button was clicked
// Buttons: WM_LBUTTONDOWN, WM_RBUTTONDOWN, WM_MBUTTONDOWN
getmouseclick(int button, int &x, int &y);  // Get click position and clear
```

### Timing and Animation

```cpp
delay(milliseconds);                // Pause execution for specified milliseconds

// Double buffering for flicker-free animation
int pages = 2;                      // Most graphics modes support 2 pages
setactivepage(0);                   // Draw on page 0
setvisualpage(1);                   // Show page 1 (user sees this)
// ...draw on page 0...
setvisualpage(0);                   // Swap: show page 0
setactivepage(1);                   // Now draw on page 1
// Repeat...
```

### Advanced Functions

```cpp
// Graphics state
int gstatus = graphresult();        // Get status of last graphics operation
// Values: grOk (0) = success, grNoInitGraph, grNotDetected, grFileNotFound, etc.
char* msg = grapherrormsg(gstatus); // Get error message string

// Graphics driver info
getmoderange(driver, &low, &high);  // Get range of valid modes for driver
getgraphmode();                     // Get current graphics mode
setgraphmode(mode);                 // Set graphics mode

// Aspect ratio
getaspectratio(&xasp, &yasp);       // Get pixel aspect ratio
setaspectratio(xasp, yasp);         // Set aspect ratio for circles/arcs

// Screen capture
unsigned size = imagesize(l,t,r,b); // Calculate buffer size for screen region
```

## Complete Function Reference

### Drawing Primitives

| Function | Description |
|----------|-------------|
| `putpixel(x, y, color)` | Draw single pixel |
| `getpixel(x, y)` | Get pixel color |
| `line(x1, y1, x2, y2)` | Draw line |
| `lineto(x, y)` | Draw line from current position |
| `linerel(dx, dy)` | Draw line relative to current position |
| `moveto(x, y)` | Move current position without drawing |
| `moverel(dx, dy)` | Move relative without drawing |
| `circle(x, y, radius)` | Draw circle |
| `arc(x, y, start, end, r)` | Draw circular arc |
| `ellipse(x, y, start, end, rx, ry)` | Draw elliptical arc |
| `rectangle(l, t, r, b)` | Draw rectangle |
| `drawpoly(n, points)` | Draw polygon from n vertices |

### Filled Shapes

| Function | Description |
|----------|-------------|
| `bar(l, t, r, b)` | Filled rectangle |
| `bar3d(l, t, r, b, depth, top)` | 3D bar |
| `fillellipse(x, y, rx, ry)` | Filled ellipse |
| `fillpoly(n, points)` | Filled polygon |
| `pieslice(x, y, start, end, r)` | Filled pie slice |
| `sector(x, y, start, end, rx, ry)` | Filled elliptical sector |
| `floodfill(x, y, border)` | Flood fill region |

### Text Functions

| Function | Description |
|----------|-------------|
| `outtextxy(x, y, str)` | Output text at position |
| `outtext(str)` | Output text at current position |
| `settextstyle(font, dir, size)` | Set text font and size |
| `settextjustify(h, v)` | Set text alignment |
| `setusercharsize(mx,dx,my,dy)` | Custom character scaling |
| `textwidth(str)` | Get text width in pixels |
| `textheight(str)` | Get text height in pixels |

### Color and Style

| Function | Description |
|----------|-------------|
| `setcolor(color)` | Set foreground color |
| `setbkcolor(color)` | Set background color |
| `setfillstyle(pattern, color)` | Set fill pattern |
| `setfillpattern(upattern, color)` | Custom fill pattern |
| `setlinestyle(style, pattern, thick)` | Set line style |
| `setwritemode(mode)` | Set logical drawing mode |
| `setpalette(index, color)` | Modify palette entry |
| `setrgbpalette(index, r, g, b)` | Set RGB palette entry |

### Viewport and Pages

| Function | Description |
|----------|-------------|
| `setviewport(l, t, r, b, clip)` | Set drawing viewport |
| `clearviewport()` | Clear viewport |
| `cleardevice()` | Clear entire screen |
| `setactivepage(page)` | Set page for drawing |
| `setvisualpage(page)` | Set visible page |

### Images

| Function | Description |
|----------|-------------|
| `imagesize(l, t, r, b)` | Calculate image buffer size |
| `getimage(l, t, r, b, buf)` | Save screen region |
| `putimage(x, y, buf, op)` | Draw saved image |

## Practical Examples

### Example 1: Animated Bouncing Ball

```cpp
#include <graphics.h>
#include <conio.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    int x = 50, y = 50;
    int dx = 2, dy = 2;
    int radius = 20;
    
    while (!kbhit()) {  // Until key press
        // Clear previous ball
        setcolor(BLACK);
        circle(x, y, radius);
        
        // Update position
        x += dx;
        y += dy;
        
        // Bounce off edges
        if (x <= radius || x >= getmaxx() - radius) dx = -dx;
        if (y <= radius || y >= getmaxy() - radius) dy = -dy;
        
        // Draw new ball
        setcolor(WHITE);
        circle(x, y, radius);
        
        delay(10);  // Control speed
    }
    
    closegraph();
    return 0;
}
```

### Example 2: Interactive Drawing Program

```cpp
#include <graphics.h>
#include <conio.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    outtextxy(10, 10, (char*)"Click to draw. Press 'c' to clear, 'q' to quit.");
    
    int prevX = -1, prevY = -1;
    
    while (true) {
        if (kbhit()) {
            char ch = getch();
            if (ch == 'q') break;
            if (ch == 'c') cleardevice();
        }
        
        if (ismouseclick(WM_LBUTTONDOWN)) {
            int x, y;
            getmouseclick(WM_LBUTTONDOWN, x, y);
            
            if (prevX != -1) {
                line(prevX, prevY, x, y);
            }
            
            prevX = x;
            prevY = y;
        }
    }
    
    closegraph();
    return 0;
}
```

### Example 3: Bar Chart

```cpp
#include <graphics.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    int data[] = {50, 80, 30, 90, 60};
    int n = 5;
    int barWidth = 60;
    int gap = 20;
    int baseY = getmaxy() - 50;
    
    for (int i = 0; i < n; i++) {
        int x = 50 + i * (barWidth + gap);
        int height = data[i] * 3;  // Scale
        
        // Draw bar
        setfillstyle(SOLID_FILL, i + 1);  // Different color for each
        bar(x, baseY - height, x + barWidth, baseY);
        
        // Draw value
        char str[10];
        sprintf(str, "%d", data[i]);
        outtextxy(x + barWidth/2 - 10, baseY - height - 20, str);
    }
    
    outtextxy(10, 10, (char*)"Sales Data");
    getch();
    closegraph();
    return 0;
}
```

### Example 4: Analog Clock

```cpp
#include <graphics.h>
#include <math.h>
#include <time.h>

#define PI 3.14159265

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    int cx = getmaxx() / 2;
    int cy = getmaxy() / 2;
    int radius = 150;
    
    while (!kbhit()) {
        cleardevice();
        
        // Draw clock face
        circle(cx, cy, radius);
        
        // Draw hour markers
        for (int i = 0; i < 12; i++) {
            double angle = i * 30 * PI / 180;
            int x1 = cx + (radius - 20) * cos(angle - PI/2);
            int y1 = cy + (radius - 20) * sin(angle - PI/2);
            int x2 = cx + radius * cos(angle - PI/2);
            int y2 = cy + radius * sin(angle - PI/2);
            line(x1, y1, x2, y2);
        }
        
        // Get current time
        time_t now = time(0);
        tm* ltm = localtime(&now);
        
        // Hour hand
        double hourAngle = (ltm->tm_hour % 12 + ltm->tm_min / 60.0) * 30 * PI / 180;
        int hx = cx + 70 * cos(hourAngle - PI/2);
        int hy = cy + 70 * sin(hourAngle - PI/2);
        setcolor(RED);
        line(cx, cy, hx, hy);
        
        // Minute hand
        double minAngle = ltm->tm_min * 6 * PI / 180;
        int mx = cx + 100 * cos(minAngle - PI/2);
        int my = cy + 100 * sin(minAngle - PI/2);
        setcolor(GREEN);
        line(cx, cy, mx, my);
        
        // Second hand
        double secAngle = ltm->tm_sec * 6 * PI / 180;
        int sx = cx + 120 * cos(secAngle - PI/2);
        int sy = cy + 120 * sin(secAngle - PI/2);
        setcolor(BLUE);
        line(cx, cy, sx, sy);
        
        delay(1000);
    }
    
    closegraph();
    return 0;
}
```

## Color Constants Reference

```cpp
// Standard 16 colors
BLACK        = 0
BLUE         = 1
GREEN        = 2
CYAN         = 3
RED          = 4
MAGENTA      = 5
BROWN        = 6
LIGHTGRAY    = 7
DARKGRAY     = 8
LIGHTBLUE    = 9
LIGHTGREEN   = 10
LIGHTCYAN    = 11
LIGHTRED     = 12
LIGHTMAGENTA = 13
YELLOW       = 14
WHITE        = 15
```

## Fill Patterns Reference

```cpp
EMPTY_FILL       = 0   // No fill
SOLID_FILL       = 1   // Solid color
LINE_FILL        = 2   // Horizontal lines
LTSLASH_FILL     = 3   // Light slashes (///)
SLASH_FILL       = 4   // Thick slashes
BKSLASH_FILL     = 5   // Back slashes (\\\)
LTBKSLASH_FILL   = 6   // Light back slashes
HATCH_FILL       = 7   // Light cross-hatch
XHATCH_FILL      = 8   // Heavy cross-hatch
INTERLEAVE_FILL  = 9   // Interleaved lines
WIDE_DOT_FILL    = 10  // Widely spaced dots
CLOSE_DOT_FILL   = 11  // Closely spaced dots
USER_FILL        = 12  // User-defined pattern
```

## Styling

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
