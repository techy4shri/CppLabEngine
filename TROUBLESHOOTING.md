# Troubleshooting Guide

So some peeps hav encountered issues while running the app so here are some of the ways to troubleshoot it. :D
Please pray and support so I build this in C++ and make it cross-platfrom (I am a student and have exams and research work to do ;-;)

---

## Wine / Linux Issues

### Error: "ImportError: DLL load failed while importing QtWidgets"

**Symptoms:**
```
wine CppLabEngine.exe
0024:err:module:import_dll Library icuuc.dll not found
0024:err:module:import_dll Library Qt6Core.dll not found
...
ImportError: DLL load failed while importing QtWidgets: Module not found.
```

**Cause:** The Windows .exe build is packaged with PyInstaller and requires native Windows. Qt6 dependencies are not compatible with Wine.

**Solution:** Run CppLabEngine from source on Linux/macOS:

```bash
# Install dependencies (Debian/Ubuntu)
sudo apt install python3 python3-pip python3-venv mingw-w64

# Or on macOS
brew install python3 mingw-w64

# Clone and run
git clone https://github.com/techy4shri/CppLabEngine.git
cd CppLabEngine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_cpplab.py
```

**Why Wine doesn't work:**
- PyInstaller bundles Python runtime but Qt6 DLLs need system libraries
- Qt6 has complex dependencies (ICU, D3D, etc.) not available in Wine
- Wine's Windows API emulation is incomplete for modern Qt6 applications

**Alternative:** Use native Linux C++ IDEs like:
- Code::Blocks with MinGW cross-compiler
- QtCreator
- VS Code with C++ extensions

---

## Windows Issues

### "Unknown Publisher" Warning

**Symptoms:** Windows Defender shows "Windows protected your PC - Unknown publisher"

**Cause:** The .exe is not code-signed with a certificate from a trusted Certificate Authority.

**Solutions:**
1. **Click "More info" → "Run anyway"** (safe if downloaded from official GitHub releases)
2. **For developers:** Sign the executable - see [SIGNING.md](SIGNING.md) for instructions
3. **For users:** Verify SHA256 checksum matches the one in release notes

### Slow Builds / Antivirus Scanning

**Symptoms:** 
- Builds take several seconds even for small files
- Disk activity spikes during compilation

**Cause:** Antivirus software scans every compiler invocation and generated .exe file.

**Solution:**
1. Add CppLabEngine folder to antivirus exclusions
2. Windows Defender: Settings → Virus & threat protection → Exclusions → Add folder
3. Example path: `C:\Users\YourName\CppLabEngine\`

### File Save Issues

**Symptoms:** Files don't save or changes are lost

**Cause:** Permissions issue or file locked by another process

**Solutions:**
1. Check file permissions (read-only?)
2. Close any external editors/viewers
3. Save As to a different location
4. Run IDE as administrator (not recommended for normal use)

### App Crashes on Launch

**Symptoms:** CppLabEngine.exe crashes immediately or shows error dialogs

**Possible Causes:**
1. **Missing Visual C++ Redistributable**: Install latest [VC++ Redist](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. **Corrupted download**: Re-download the .zip and extract to new location
3. **Path with special characters**: Move to simple path like `C:\CppLabEngine`
4. **Antivirus blocking**: Temporarily disable antivirus during first launch

**Debug steps:**
1. Check Windows Event Viewer for crash details
2. Try running from command prompt to see error messages:
   ```cmd
   cd C:\path\to\CppLabEngine
   CppLabEngine.exe
   ```

---

## Build Issues

### "Toolchains Not Found" Warning

**Symptoms:** Build menu is disabled, warning about missing MinGW

**Cause:** Compiler toolchains not found in `compilers/` directory

**Solution:**
1. Ensure `compilers/mingw32/` and `compilers/mingw64/` exist
2. Check that `bin/gcc.exe` and `bin/g++.exe` are present in each
3. Re-extract the full release archive (don't copy just the .exe)
4. For custom setup, see [BUILDING.md](BUILDING.md)

### Graphics Programs Won't Build

**Symptoms:** `undefined reference to 'initgraph'` or similar graphics.h errors

**Cause:** Missing 32-bit MinGW or WinBGIm libraries

**Requirements:**
- Must use 32-bit toolchain (mingw32)
- WinBGIm libraries must be in `compilers/mingw32/lib/`
- Libraries: `libbgi.a`, `libgdi32.a`, `libcomdlg32.a`, etc.

**Solution:**
1. Ensure project uses "Graphics Application" type
2. Or for console project: Enable graphics feature in `.cpplab.json`
3. Verify files exist:
   ```
   compilers/mingw32/lib/libbgi.a
   compilers/mingw32/include/graphics.h
   ```

### OpenMP Programs Won't Build

**Symptoms:** `#pragma omp` directives ignored or `omp.h` not found

**Cause:** Using 32-bit toolchain or OpenMP not enabled

**Requirements:**
- Must use 64-bit toolchain (mingw64) - better OpenMP support
- OpenMP feature must be enabled

**Solution:**
1. Use "Console Application" with OpenMP enabled
2. Or manually enable in `.cpplab.json`:
   ```json
   "features": {
     "openmp": true
   }
   ```
3. Select "64-bit (mingw64)" in toolbar

---

## Runtime Issues

### Program Input Not Working

**Symptoms:** Programs using `cin`, `scanf()`, `getchar()` don't accept input

**Solution (v1.0.0+):** All programs now run in external terminal by default
- Press F5 or Build → Run to launch in new cmd window
- Input works normally in the terminal
- Close terminal window when done

**Old versions:** Update to latest release

### Graphics Window Doesn't Appear

**Symptoms:** Program compiles but no graphics window shows

**Possible Causes:**
1. **Wrong toolchain**: Graphics requires 32-bit MinGW
2. **Missing DLLs**: Graphics libraries not linked
3. **Code error**: Check `initgraph()` return value

**Debug:**
```cpp
#include <graphics.h>
int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    if (graphresult() != grOk) {
        printf("Graphics error: %s\n", grapherrormsg(graphresult()));
        return 1;
    }
    
    // Your graphics code here
    
    getch();
    closegraph();
    return 0;
}
```

### Program Runs but Terminal Closes Immediately

**Symptoms:** Can't see program output, terminal flashes and closes

**Cause:** This is by design - programs are launched with `cmd /k` which keeps window open

**If it still closes:** Add pause at end of your code:
```cpp
// C++
std::cout << "\nPress Enter to exit...";
std::cin.get();

// C
printf("\nPress Enter to exit...");
getchar();
```

---

## Compilation Errors

### "File not found" or Path Issues

**Symptoms:** Compiler can't find source files or headers

**Solutions:**
1. **Avoid spaces in paths**: Use `C:\Projects\MyCode` not `C:\My Projects\My Code`
2. **Avoid special characters**: Don't use `@`, `#`, `&`, etc. in folder/file names
3. **Check case sensitivity**: `Main.cpp` vs `main.cpp` matters
4. **Relative paths**: Headers should use relative includes: `#include "header.h"`

### "Permission Denied" Building

**Symptoms:** `gcc.exe: error: CreateProcess: Permission denied`

**Cause:** Antivirus is quarantining or blocking gcc.exe

**Solution:**
1. Add `compilers/` folder to antivirus exclusions
2. Temporarily disable real-time protection
3. Check antivirus quarantine and restore gcc.exe

### Undefined Reference Errors

**Symptoms:** `undefined reference to 'function_name'`

**Common Causes:**
1. **Missing library**: Add `-l` flag (e.g., `-lbgi` for graphics)
2. **Linking order**: Libraries should come after source files
3. **Wrong standard**: Some functions need specific C/C++ standard

**For graphics.h:**
Ensure project type is "Graphics Application" or manually add:
```
-lbgi -lgdi32 -lcomdlg32 -luuid -lole32 -loleaut32
```

---

## UI Issues

### Syntax Highlighting Slow or Frozen

**Symptoms:** Editor freezes when typing in large files

**Cause:** Syntax highlighter processes entire document on every keystroke

**Workaround:**
1. Close other tabs to reduce memory usage
2. Split large files into smaller modules
3. Disable syntax highlighting (not yet implemented - feature request)

### Problems Table Not Updating

**Symptoms:** Errors persist after fixing code

**Solution:** Rebuild the project (F7) - diagnostics update on build, not on save

---

## Getting Help

If your issue isn't listed here:

1. **Check existing issues**: [GitHub Issues](https://github.com/techy4shri/CppLabEngine/issues)
2. **Search discussions**: [GitHub Discussions](https://github.com/techy4shri/CppLabEngine/discussions)
3. **Ask for help**: Open a new issue with:
   - OS version (Windows 10/11)
   - CppLabEngine version
   - Steps to reproduce
   - Screenshots/error messages
   - Minimal code example that fails

---

**Remember:** This is an educational tool designed for Windows college lab environments. For production development, consider professional IDEs like Visual Studio, CLion, or VS Code.
