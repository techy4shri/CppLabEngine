# Utility functions for UI resource loading in both dev and frozen (PyInstaller) modes.

import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent  # points to cpplab/


def ui_path(name: str) -> str:
    """
    Return an absolute path to a .ui file, both in development and when frozen.

    In dev:   <repo>/src/cpplab/ui/<name>
    Frozen:   <dist>/CppLabEngine/_internal/cpplab/ui/<name>

    Args:
        name: The .ui filename (e.g., "MainWindow.ui")

    Returns:
        Absolute path to the .ui file as a string
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller frozen mode
        base = Path(sys._MEIPASS) / "cpplab" / "ui"
    else:
        # Development mode
        base = HERE / "ui"
    return str(base / name)


def resource_path(name: str) -> Path:
    """
    Return an absolute path to a resource file, both in development and when frozen.

    In dev:   <repo>/src/cpplab/resources/<name>
    Frozen:   <dist>/CppLabEngine/_internal/cpplab/resources/<name>

    Args:
        name: The resource filename (e.g., "logo.png")

    Returns:
        Absolute Path to the resource file
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller frozen mode
        base = Path(sys._MEIPASS) / "cpplab" / "resources"
    else:
        # Development mode
        base = HERE / "resources"
    return base / name

