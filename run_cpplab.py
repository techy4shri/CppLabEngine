"""
Light-weight runner that ensures `src` is on sys.path and launches the application.

Run with:
    python run_cpplab.py

This is helpful when running from the repository root without installing the package.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

def main():
    # Import the package entry point and run
    from cpplab.main import main as cpplab_main
    cpplab_main()

if __name__ == "__main__":
    main()
