"""
Test script to verify project structure and imports
Run this before attempting to launch the IDE
"""

import sys
from pathlib import Path

def test_imports():
    print("Testing imports...")
    errors = []
    
    try:
        import PyQt6
        print("  ✓ PyQt6 installed")
    except ImportError as e:
        errors.append(f"  ✗ PyQt6 not found: {e}")
    
    try:
        from PyQt6 import QtWidgets, QtGui, QtCore
        print("  ✓ PyQt6 modules accessible")
    except ImportError as e:
        errors.append(f"  ✗ PyQt6 modules not accessible: {e}")
    
    try:
        from PyQt6 import uic
        print("  ✓ PyQt6.uic available")
    except ImportError as e:
        errors.append(f"  ✗ PyQt6.uic not available: {e}")
    
    return errors

def test_structure():
    print("\nTesting project structure...")
    errors = []
    
    required_files = [
        "src/cpplab/__init__.py",
        "src/cpplab/main.py",
        "src/cpplab/app.py",
        "src/cpplab/dialogs.py",
        "src/cpplab/ui/MainWindow.ui",
        "src/cpplab/ui/NewProjectDialog.ui",
        "src/cpplab/widgets/__init__.py",
        "src/cpplab/widgets/code_editor.py",
        "src/cpplab/widgets/project_explorer.py",
        "src/cpplab/widgets/output_panel.py",
        "src/cpplab/core/__init__.py",
        "src/cpplab/core/project_config.py",
        "src/cpplab/core/toolchains.py",
        "src/cpplab/core/builder.py",
        "src/cpplab/core/docs.py",
    ]
    
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            errors.append(f"  ✗ Missing: {file_path}")
    
    return errors

def test_module_imports():
    print("\nTesting module imports...")
    errors = []
    
    # Add src to path temporarily
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from cpplab.core import project_config
        print("  ✓ project_config module")
    except ImportError as e:
        errors.append(f"  ✗ project_config: {e}")
    
    try:
        from cpplab.core import toolchains
        print("  ✓ toolchains module")
    except ImportError as e:
        errors.append(f"  ✗ toolchains: {e}")
    
    try:
        from cpplab.core import builder
        print("  ✓ builder module")
    except ImportError as e:
        errors.append(f"  ✗ builder: {e}")
    
    try:
        from cpplab.widgets import code_editor
        print("  ✓ code_editor module")
    except ImportError as e:
        errors.append(f"  ✗ code_editor: {e}")
    
    try:
        from cpplab.widgets import project_explorer
        print("  ✓ project_explorer module")
    except ImportError as e:
        errors.append(f"  ✗ project_explorer: {e}")
    
    try:
        from cpplab.widgets import output_panel
        print("  ✓ output_panel module")
    except ImportError as e:
        errors.append(f"  ✗ output_panel: {e}")
    
    sys.path.pop(0)
    return errors

def main():
    print("=" * 50)
    print("CppLabEngine - Pre-launch Tests")
    print("=" * 50)
    
    all_errors = []
    
    all_errors.extend(test_imports())
    all_errors.extend(test_structure())
    all_errors.extend(test_module_imports())
    
    print("\n" + "=" * 50)
    if all_errors:
        print("TESTS FAILED")
        print("=" * 50)
        for error in all_errors:
            print(error)
        print("\nPlease fix these issues before running the IDE.")
        return 1
    else:
        print("ALL TESTS PASSED")
        print("=" * 50)
        print("\nYou can now run the IDE:")
        print("  python -m cpplab.main")
        print("  or: launch.bat")
        return 0

if __name__ == "__main__":
    sys.exit(main())
