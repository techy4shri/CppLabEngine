# Application entry point.

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from .app import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CppLab IDE")
    app.setOrganizationName("CppLab")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
