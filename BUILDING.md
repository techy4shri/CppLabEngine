# Building CppLabEngine

This document provides detailed instructions for building CppLabEngine from source.

## Quick Build

For a quick build on Windows:

```powershell
.\build.ps1
```

## Prerequisites

### Required Software

- **Python 3.13+** - Download from [python.org](https://www.python.org/)
- **PowerShell** - Built into Windows 10/11
- **Git** (optional) - For cloning the repository

### Required Resources (Not in Git)

The following directories are required but not included in the repository:

1. **`compilers/`** - MinGW toolchains
   - `compilers/mingw32/` - 32-bit MinGW with WinBGIm graphics library
   - `compilers/mingw64/` - 64-bit MinGW with OpenMP support

2. **`examples/`** (optional) - Sample projects for users

3. **`licenses/`** (optional) - Third-party license files

## Build Process Details

### What the Build Script Does

The `build.ps1` script performs these steps:

1. **Clean** - Removes previous `dist/`, `build/`, and `.spec` files
2. **Environment** - Creates/activates Python virtual environment (`.venv`)
3. **Dependencies** - Installs from `requirements.txt` and PyInstaller
4. **PyInstaller** - Builds executable with these options:
   - `--onedir` - Creates directory with executable and dependencies
   - `--windowed` - No console window (GUI app)
   - `--name CppLabEngine` - Sets executable name
   - `--add-data` - Bundles UI files and documentation
5. **Resources** - Copies compilers, examples, licenses, README, LICENSE
6. **Archive** - Creates `CppLabEngine-v0.1.0-win64.zip` in `dist/`

### Output Structure

After building, you'll have:

```
dist/
├── CppLabEngine/
│   ├── CppLabEngine.exe          # Main executable
│   ├── _internal/             # Python runtime and dependencies
│   ├── cpplab/
│   │   └── ui/                # UI files (.ui)
│   ├── docs_source/           # Markdown documentation
│   ├── compilers/             # MinGW toolchains
│   │   ├── mingw32/
│   │   └── mingw64/
│   ├── examples/              # Sample projects
│   ├── licenses/              # Third-party licenses
│   ├── LICENSE                # Main license
│   └── README.md              # User documentation
└── CppLabEngine-v0.1.0-win64.zip # Distribution archive
```

## Manual Build Steps

If you prefer to build manually or need to customize:

### 1. Setup Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

### 2. Run PyInstaller

```powershell
pyinstaller --onedir `
    --name CppLabEngine `
    --windowed `
    --noconfirm `
    --clean `
    --add-data "src/cpplab/ui;cpplab/ui" `
    --add-data "docs_source;docs_source" `
    src/cpplab/main.py
```

### 3. Copy Resources

```powershell
# Copy compilers
Copy-Item -Recurse -Force compilers dist\CppLabEngine\compilers

# Copy examples (if exists)
Copy-Item -Recurse -Force examples dist\CppLabEngine\examples

# Copy licenses (if exists)
Copy-Item -Recurse -Force licenses dist\CppLabEngine\licenses

# Copy LICENSE and README
Copy-Item -Force LICENSE dist\CppLabEngine\LICENSE
Copy-Item -Force README.md dist\CppLabEngine\README.md
```

### 4. Create Archive

```powershell
Compress-Archive -Path dist\CppLabEngine -DestinationPath dist\CppLabEngine-v0.1.0-win64.zip
```

## Customizing the Build

### Changing Version Number

Edit `build.ps1` and change:

```powershell
$VERSION = "0.1.0"  # Change to your version
```

### Adding More Resources

To include additional files in the distribution, add to the "Copy resources" section:

```powershell
# In build.ps1, after Step 5
if (Test-Path "your_folder") {
    Copy-Item -Recurse -Force "your_folder" "$DIST_DIR\$APP_NAME\your_folder"
}
```

### PyInstaller Options

Common options you might want to add:

- `--icon myicon.ico` - Set application icon
- `--version-file version.txt` - Add version info (Windows)
- `--add-data "src;dest"` - Bundle additional data files
- `--hidden-import module` - Include modules not auto-detected
- `--exclude-module module` - Exclude unnecessary modules

## Troubleshooting

### "Cannot run scripts" Error

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Missing compilers/ Directory

The script will warn but continue. To include compilers:

1. Download MinGW-w64 distributions
2. Extract to `compilers/mingw32` and `compilers/mingw64`
3. Ensure WinBGIm libraries are in mingw32

### PyInstaller Warnings

PyInstaller may show warnings about missing modules. These are usually safe to ignore if the application runs correctly.

### Large Archive Size

The distribution includes:
- Python runtime (~50-100 MB)
- PyQt6 libraries (~50-80 MB)
- MinGW compilers (~200-400 MB each)

Total size is typically 500-800 MB compressed.

## Testing the Build

After building:

1. **Test locally:**
   ```powershell
   .\dist\CppLabEngine\CppLabEngine.exe
   ```

2. **Test on clean system:**
   - Copy `dist/CppLabEngine/` to another Windows machine
   - Run `CppLabEngine.exe` (no Python installation required)

3. **Test project creation:**
   - Create a new console project
   - Create a graphics project
   - Build and run both

## Distributing

The `CppLabEngine-v0.1.0-win64.zip` file contains everything needed:

1. Upload to releases page on GitHub
2. Users download and extract
3. Run `CppLabEngine.exe` - no installation required

## Build Environment

Tested on:
- Windows 10/11
- Python 3.13.5
- PyQt6 6.6.0
- PyInstaller 6.x

## See Also

- [README.md](README.md) - General project information
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guidelines
- [requirements.txt](requirements.txt) - Python dependencies
