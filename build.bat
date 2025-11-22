@echo off
REM Build script for CppLab IDE distribution

echo ========================================
echo CppLab IDE Build Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    exit /b 1
)

echo [1/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo [2/5] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    exit /b 1
)

echo.
echo [3/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [4/5] Building executable with PyInstaller...
pyinstaller cpplab.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    exit /b 1
)

echo.
echo [5/5] Copying compilers to distribution...
if exist compilers (
    xcopy /E /I /Y compilers dist\CppLabIDE\compilers
    echo Compilers copied successfully
) else (
    echo WARNING: compilers/ directory not found
    echo Please add MinGW toolchains before distribution
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Output directory: dist\CppLabIDE\
echo Executable: dist\CppLabIDE\CppLabIDE.exe
echo.
echo Next steps:
echo 1. Add MinGW toolchains to dist\CppLabIDE\compilers\
echo 2. Test the executable
echo 3. Create installer or zip for distribution
echo.
pause
