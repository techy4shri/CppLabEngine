# Release build script for CppLabEngine.
# Creates a portable Windows distribution with PyInstaller.

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "CppLabEngine"
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")
ROOT_DIR = Path(__file__).parent.parent


def print_step(step_num, total, message):
    """Print colored step header."""
    print(f"\n{'='*70}")
    print(f"[{step_num}/{total}] {message}")
    print(f"{'='*70}\n")


def clean_build():
    """Remove previous build artifacts."""
    print_step(1, 6, "Cleaning previous builds")
    
    for path in [DIST_DIR, BUILD_DIR]:
        if path.exists():
            print(f"  Removing {path}/")
            shutil.rmtree(path)
    
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"
    if spec_file.exists():
        print(f"  Removing {spec_file}")
        spec_file.unlink()
    
    print("  Clean complete ✓")


def run_pyinstaller():
    """Build executable with PyInstaller."""
    print_step(2, 6, "Building executable with PyInstaller")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name", APP_NAME,
        "--onedir",
        "--windowed",
        "--add-data", "src/cpplab/ui;cpplab/ui",
        "--add-data", "src/cpplab/resources;cpplab/resources",
        "--add-data", "docs_source;docs_source",
        "src/cpplab/main.py"
    ]
    
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    
    if result.returncode != 0:
        print("\n  ERROR: PyInstaller failed!")
        sys.exit(1)
    
    print("  Executable built ✓")


def copy_resources():
    """Copy compilers, examples, and licenses to distribution."""
    print_step(3, 6, "Copying resources")
    
    dist_root = DIST_DIR / APP_NAME
    
    # Copy compilers (required)
    compilers_src = ROOT_DIR / "compilers"
    compilers_dst = dist_root / "compilers"
    if compilers_src.exists():
        print(f"  Copying compilers/")
        shutil.copytree(compilers_src, compilers_dst, dirs_exist_ok=True)
    else:
        print("  WARNING: compilers/ not found (required for distribution!)")
    
    # Copy examples (optional)
    examples_src = ROOT_DIR / "examples"
    examples_dst = dist_root / "examples"
    if examples_src.exists():
        print(f"  Copying examples/")
        shutil.copytree(examples_src, examples_dst, dirs_exist_ok=True)
    else:
        print("  WARNING: examples/ not found (skipping)")
    
    # Create licenses directory
    licenses_dst = dist_root / "licenses"
    licenses_dst.mkdir(exist_ok=True)
    
    # Copy LICENSE file
    license_src = ROOT_DIR / "LICENSE"
    if license_src.exists():
        print(f"  Copying LICENSE")
        shutil.copy2(license_src, licenses_dst / "CppLabEngine_LICENSE.txt")
    
    # Create placeholder license files for bundled components
    print("  Creating license placeholders")
    
    (licenses_dst / "MinGW_LICENSE.txt").write_text(
        "MinGW-w64 Compiler Collection\n"
        "License: Multiple (GCC: GPL, Runtime: Public Domain/MIT)\n\n"
        "This distribution includes MinGW-w64 compilers.\n"
        "Full license information: https://www.mingw-w64.org/\n\n"
        "GCC (GNU Compiler Collection) is licensed under GPL v3+\n"
        "Runtime libraries are under runtime exception or more permissive licenses.\n"
    )
    
    (licenses_dst / "WinBGIm_LICENSE.txt").write_text(
        "WinBGIm - Windows BGI Implementation\n"
        "License: BSD-style\n\n"
        "WinBGIm is provided for educational purposes.\n"
        "Original BGI graphics library by Borland.\n"
        "Windows port by various contributors.\n\n"
        "For more information: http://www.cs.colorado.edu/~main/cs1300/doc/bgi/\n"
    )
    
    (licenses_dst / "PyQt6_LICENSE.txt").write_text(
        "PyQt6 - Python bindings for Qt6\n"
        "License: GPL v3 / Commercial\n\n"
        "This application uses PyQt6 under the GPL v3 license.\n"
        "PyQt6 is developed by Riverbank Computing Limited.\n\n"
        "Qt6 is licensed under LGPL v3 / Commercial by The Qt Company.\n\n"
        "For more information:\n"
        "  PyQt: https://riverbankcomputing.com/software/pyqt/\n"
        "  Qt: https://www.qt.io/licensing/\n"
    )
    
    print("  Resources copied ✓")


def create_readme():
    """Create end-user README.txt."""
    print_step(4, 6, "Creating README.txt")
    
    readme_content = f"""CppLabEngine v{VERSION}
{'='*70}

An offline C/C++ IDE for Windows with bundled compilers and graphics support.

FEATURES
--------
- Console and graphics-based C/C++ projects
- Support for C11, C++11/14/17/20 standards
- graphics.h library (via 32-bit MinGW with WinBGIm)
- OpenMP parallel computing (64-bit MinGW)
- Standalone source file mode (no project needed)
- Syntax highlighting and project management
- Bundled MinGW 32-bit and 64-bit toolchains

REQUIREMENTS
------------
- Windows 10 or Windows 11 (64-bit)
- No additional software needed (compilers included)

INSTALLATION
------------
1. Extract this folder anywhere on your computer
   (e.g., C:\\CppLabEngine or D:\\Programs\\CppLabEngine)

2. Double-click CppLabEngine.exe to start

No admin rights required after extraction.
No installation needed - the app is fully portable.

IMPORTANT NOTES
---------------
- First launch may be slow while Windows scans the files
- Builds may be slow if your antivirus scans every compile
  
  RECOMMENDED: Add the CppLabEngine folder to your antivirus exclusions
  for faster build performance.

- The compilers/ folder contains MinGW toolchains (required)
- The examples/ folder contains sample projects

GETTING STARTED
---------------
1. Create a new project: File → New Project
2. Choose language (C or C++) and standard
3. Select project type:
   - Console Application (general purpose)
   - Graphics Application (uses graphics.h)
4. Write your code in the editor
5. Press F7 to build, or F5 to build and run

STANDALONE FILE MODE
--------------------
To quickly compile a single .c or .cpp file without creating a project:

1. File → Open File
2. Edit your code
3. Press F7 (Build) or F5 (Build & Run)

The IDE will automatically detect:
- graphics.h usage → adds graphics libraries
- OpenMP pragmas → enables OpenMP support

TROUBLESHOOTING
---------------
- If exe crashes: Try running from a path without spaces or special characters
- If builds fail: Check that compilers/ folder exists with mingw32/ and mingw64/
- If graphics don't work: Graphics requires 32-bit MinGW (mingw32/)
- Slow builds: Add CppLabEngine folder to antivirus exclusions

DOCUMENTATION
-------------
Help → Offline Documentation (opens in browser)

SUPPORT
-------
GitHub: https://github.com/techy4shri/CppLabEngine
Issues: https://github.com/techy4shri/CppLabEngine/issues

LICENSE
-------
See licenses/ folder for CppLabEngine and bundled component licenses.

© 2025 CppLab Project
"""
    
    readme_path = DIST_DIR / APP_NAME / "README.txt"
    readme_path.write_text(readme_content, encoding='utf-8')
    
    print(f"  Created {readme_path} ✓")


def create_archives():
    """Create release archives (both .zip and .7z)."""
    print_step(5, 7, "Creating release archives")
    
    dist_folder = DIST_DIR / APP_NAME
    
    # Create standard .zip (maximum compatibility)
    print(f"  Creating .zip archive (standard compression)...")
    zip_name = f"{APP_NAME}-v{VERSION}-windows-x64.zip"
    zip_path = DIST_DIR / zip_name
    
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file_path in dist_folder.rglob('*'):
            if file_path.is_file():
                arc_name = file_path.relative_to(DIST_DIR)
                zf.write(file_path, arc_name)
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"    ✓ {zip_path.name} ({zip_size_mb:.1f} MB)")
    
    # Create .7z archive (better compression, requires 7-Zip)
    print(f"\n  Creating .7z archive (ultra compression)...")
    sevenz_name = f"{APP_NAME}-v{VERSION}-windows-x64.7z"
    sevenz_path = DIST_DIR / sevenz_name
    
    if sevenz_path.exists():
        sevenz_path.unlink()
    
    # Try to use 7z command line
    sevenz_cmd = shutil.which("7z")
    if not sevenz_cmd:
        # Try common installation paths
        possible_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        for path in possible_paths:
            if Path(path).exists():
                sevenz_cmd = path
                break
    
    if sevenz_cmd:
        try:
            result = subprocess.run(
                [sevenz_cmd, "a", "-t7z", "-mx=9", "-ms=on", str(sevenz_path), str(dist_folder)],
                cwd=DIST_DIR,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                sevenz_size_mb = sevenz_path.stat().st_size / (1024 * 1024)
                compression_ratio = (1 - sevenz_size_mb / zip_size_mb) * 100
                print(f"    ✓ {sevenz_path.name} ({sevenz_size_mb:.1f} MB, {compression_ratio:.1f}% smaller)")
            else:
                print(f"    ✗ 7z compression failed: {result.stderr}")
                print("    → Only .zip archive will be available")
        except Exception as e:
            print(f"    ✗ 7z compression error: {e}")
            print("    → Only .zip archive will be available")
    else:
        print(f"    ⚠ 7-Zip not found (install from https://www.7-zip.org/)")
        print("    → Only .zip archive will be available")
    
    print(f"\n  Archive creation complete ✓")


def summary():
    """Print build summary."""
    print_step(7, 7, "Build Summary")
    
    dist_folder = DIST_DIR / APP_NAME
    zip_path = DIST_DIR / f"{APP_NAME}-v{VERSION}-windows-x64.zip"
    sevenz_path = DIST_DIR / f"{APP_NAME}-v{VERSION}-windows-x64.7z"
    
    print("  Output files:")
    print(f"    • Executable: dist/{APP_NAME}/{APP_NAME}.exe")
    
    if zip_path.exists():
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"    • ZIP Archive: {zip_path.name} ({size_mb:.1f} MB)")
    
    if sevenz_path.exists():
        size_mb = sevenz_path.stat().st_size / (1024 * 1024)
        print(f"    • 7Z Archive: {sevenz_path.name} ({size_mb:.1f} MB)")
    
    print("\n  Upload to GitHub Release:")
    print(f"    1. Primary: {zip_path.name} (everyone can open)")
    if sevenz_path.exists():
        print(f"    2. Optional: {sevenz_path.name} (smaller, requires 7-Zip)")
    
    print("\n  ✓ Build complete!")
    """Verify the build output."""
    print_step(6, 7, "Verifying build")
    
    dist_folder = DIST_DIR / APP_NAME
    exe_path = dist_folder / f"{APP_NAME}.exe"
    
    checks = [
        (exe_path, "Executable"),
        (dist_folder / "_internal" / "cpplab" / "ui", "UI files"),
        (dist_folder / "_internal" / "cpplab" / "resources", "Resources"),
        (dist_folder / "docs_source", "Documentation"),
        (dist_folder / "compilers", "Compilers"),
        (dist_folder / "licenses", "Licenses"),
        (dist_folder / "README.txt", "README"),
    ]
    
    all_ok = True
    for path, name in checks:
        if path.exists():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: MISSING at {path}")
            all_ok = False
    
    if not all_ok:
        print("\n  WARNING: Some components are missing from the distribution!")
    else:
        print("\n  All components present ✓")
    
    return all_ok


def main():
    """Main build process."""
    print(f"\n{'='*70}")
    print(f"Building {APP_NAME} v{VERSION} for Windows")
    print(f"{'='*70}\n")
    
    os.chdir(ROOT_DIR)
    
    try:
        clean_build()
        run_pyinstaller()
        copy_resources()
        create_readme()
        create_archives()
        verify_build()
        summary()
        
        print(f"\n{'='*70}")
        print("SUCCESS!")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"BUILD FAILED: {e}")
        print(f"{'='*70}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
