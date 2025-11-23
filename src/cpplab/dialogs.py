# Dialog for creating new projects.

import os
import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog
from .core.toolchains import get_app_root


class NewProjectDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load UI (works in both dev and frozen modes)
        if getattr(sys, 'frozen', False):
            ui_path = get_app_root() / "cpplab" / "ui" / "NewProjectDialog.ui"
        else:
            ui_path = Path(__file__).parent / "ui" / "NewProjectDialog.ui"
        uic.loadUi(ui_path, self)
        
        self.editLocation.setText(str(Path.home() / "CppLabProjects"))
        
        self._connect_signals()
        self._update_standard_options()
    
    def _connect_signals(self):
        self.btnBrowse.clicked.connect(self._on_browse)
        self.comboLanguage.currentTextChanged.connect(self._update_standard_options)
        self.radioConsole.toggled.connect(self._on_project_type_changed)
        self.radioGraphics.toggled.connect(self._on_project_type_changed)
        self.checkGraphics.toggled.connect(self._on_graphics_toggled)
    
    def _on_browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Location")
        if directory:
            self.editLocation.setText(directory)
    
    def _update_standard_options(self):
        language = self.comboLanguage.currentText()
        self.comboStandard.clear()
        
        if language == "C++":
            self.comboStandard.addItems(["c++20", "c++17", "c++14", "c++11"])
        else:
            self.comboStandard.addItems(["c11", "c99", "c89"])
    
    def _on_project_type_changed(self):
        if self.radioGraphics.isChecked():
            self.checkGraphics.setEnabled(False)
            self.checkGraphics.setChecked(True)
            self.checkOpenMP.setEnabled(False)
            self.checkOpenMP.setChecked(False)
        else:
            self.checkGraphics.setEnabled(True)
            self.checkOpenMP.setEnabled(not self.checkGraphics.isChecked())
    
    def _on_graphics_toggled(self, checked: bool):
        if checked:
            self.checkOpenMP.setChecked(False)
            self.checkOpenMP.setEnabled(False)
        else:
            self.checkOpenMP.setEnabled(True)
    
    def get_project_data(self) -> dict:
        language = "cpp" if self.comboLanguage.currentText() == "C++" else "c"
        standard = self.comboStandard.currentText()
        
        if self.radioGraphics.isChecked():
            project_type = "graphics"
            enable_graphics = True
            enable_openmp = False
        else:
            project_type = "console"
            enable_graphics = self.checkGraphics.isChecked()
            enable_openmp = self.checkOpenMP.isChecked()
        
        return {
            "name": self.editProjectName.text().strip(),
            "parent_dir": self.editLocation.text().strip(),
            "language": language,
            "standard": standard,
            "project_type": project_type,
            "enable_graphics": enable_graphics,
            "enable_openmp": enable_openmp
        }
