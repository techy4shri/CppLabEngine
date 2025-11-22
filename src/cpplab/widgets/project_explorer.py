# Project explorer tree widget for navigating project files.

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
from typing import Optional
from ..core.project_config import ProjectConfig


class ProjectExplorer(QTreeWidget):
    
    file_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_config: Optional[ProjectConfig] = None
        
        self.setHeaderLabel("Project Explorer")
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def load_project(self, project_config: ProjectConfig):
        self.project_config = project_config
        self.clear()
        
        root_item = QTreeWidgetItem([project_config.name])
        self.addTopLevelItem(root_item)
        root_item.setExpanded(True)
        
        for file_path in project_config.files:
            file_item = QTreeWidgetItem([Path(file_path).name])
            file_item.setData(0, 0x0100, file_path)
            root_item.addChild(file_item)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        file_rel_path = item.data(0, 0x0100)
        if file_rel_path and self.project_config:
            full_path = str(Path(self.project_config.path) / file_rel_path)
            self.file_double_clicked.emit(full_path)
