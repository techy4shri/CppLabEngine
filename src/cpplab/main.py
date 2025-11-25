# Application entry point.

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from .app import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CppLabEngine")
    app.setOrganizationName("CppLabEngine")
    
    # Set application icon
    icon_path = Path(__file__).parent / "resources"/ "logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
