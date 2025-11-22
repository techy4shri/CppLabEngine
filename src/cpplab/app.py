# Main application window controller.

import os
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QWidget
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional
from .core.project_config import ProjectConfig, create_new_project
from .core.builder import build_project, run_project, BuildResult
from .widgets.code_editor import CodeEditor
from .widgets.project_explorer import ProjectExplorer
from .widgets.output_panel import OutputPanel


class BuildThread(QThread):
    
    build_finished = pyqtSignal(object)
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
    
    def run(self):
        result = build_project(self.project_config)
        self.build_finished.emit(result)


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[ProjectConfig] = None
        self.build_thread: Optional[BuildThread] = None
        
        ui_path = Path(__file__).parent / "ui" / "MainWindow.ui"
        uic.loadUi(ui_path, self)
        
        self._setup_widgets()
        self._connect_signals()
    
    def _setup_widgets(self):
        self.project_explorer = ProjectExplorer()
        left_panel_layout = self.leftPanel.layout()
        left_panel_layout.addWidget(self.project_explorer)
        self.leftPanel.findChild(QWidget, "projectExplorer").deleteLater()
        
        self.output_panel = OutputPanel()
        self.outputPanel.deleteLater()
        self.rightSplitter.addWidget(self.output_panel)
    
    def _connect_signals(self):
        self.actionNewProject.triggered.connect(self._on_new_project)
        self.actionOpenProject.triggered.connect(self._on_open_project)
        self.actionSave.triggered.connect(self._on_save)
        self.actionSaveAll.triggered.connect(self._on_save_all)
        self.actionExit.triggered.connect(self.close)
        
        self.actionBuild.triggered.connect(self._on_build)
        self.actionRun.triggered.connect(self._on_run)
        self.actionBuildAndRun.triggered.connect(self._on_build_and_run)
        
        self.actionAbout.triggered.connect(self._on_about)
        
        self.project_explorer.file_double_clicked.connect(self._open_file_in_editor)
        self.editorTabs.tabCloseRequested.connect(self._close_editor_tab)
    
    def _on_new_project(self):
        from .dialogs import NewProjectDialog
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_data = dialog.get_project_data()
            try:
                project = create_new_project(**project_data)
                self._load_project(project)
                
                main_file_path = Path(project.path) / project.main_file
                self._open_file_in_editor(str(main_file_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")
    
    def _on_open_project(self):
        project_dir = QFileDialog.getExistingDirectory(self, "Open Project")
        if project_dir:
            config_file = Path(project_dir) / ".cpplab.json"
            if not config_file.exists():
                QMessageBox.warning(self, "Warning", "Not a valid CppLab project directory.")
                return
            try:
                project = ProjectConfig.load(project_dir)
                self._load_project(project)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project: {str(e)}")
    
    def _load_project(self, project: ProjectConfig):
        self.current_project = project
        self.project_explorer.load_project(project)
        self.setWindowTitle(f"CppLab IDE - {project.name}")
    
    def _open_file_in_editor(self, file_path: str):
        for i in range(self.editorTabs.count()):
            editor = self.editorTabs.widget(i)
            if isinstance(editor, CodeEditor) and editor.file_path == file_path:
                self.editorTabs.setCurrentIndex(i)
                return
        
        editor = CodeEditor()
        editor.load_file(file_path)
        tab_name = Path(file_path).name
        self.editorTabs.addTab(editor, tab_name)
        self.editorTabs.setCurrentWidget(editor)
    
    def _close_editor_tab(self, index: int):
        editor = self.editorTabs.widget(index)
        if isinstance(editor, CodeEditor) and editor.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"Save changes to {Path(editor.file_path).name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                editor.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.editorTabs.removeTab(index)
    
    def _on_save(self):
        current_editor = self.editorTabs.currentWidget()
        if isinstance(current_editor, CodeEditor):
            current_editor.save_file()
            index = self.editorTabs.currentIndex()
            tab_name = Path(current_editor.file_path).name
            self.editorTabs.setTabText(index, tab_name)
    
    def _on_save_all(self):
        for i in range(self.editorTabs.count()):
            editor = self.editorTabs.widget(i)
            if isinstance(editor, CodeEditor) and editor.is_modified:
                editor.save_file()
                tab_name = Path(editor.file_path).name
                self.editorTabs.setTabText(i, tab_name)
    
    def _on_build(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please open a project first.")
            return
        
        self._on_save_all()
        
        self.output_panel.clear_output()
        self.output_panel.append_output("=== Build Started ===")
        
        self.build_thread = BuildThread(self.current_project)
        self.build_thread.build_finished.connect(self._on_build_finished)
        self.build_thread.start()
    
    def _on_build_finished(self, result: BuildResult):
        self.output_panel.append_output(f"\nCommand: {result.command}\n")
        
        if result.stdout:
            self.output_panel.append_output(result.stdout)
        if result.stderr:
            self.output_panel.append_output(result.stderr)
        
        if result.success:
            self.output_panel.append_output("\n=== Build Succeeded ===")
        else:
            self.output_panel.append_output("\n=== Build Failed ===")
    
    def _on_run(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please open a project first.")
            return
        
        exe_path = self.current_project.get_output_executable()
        if not Path(exe_path).exists():
            QMessageBox.warning(self, "No Executable", "Please build the project first.")
            return
        
        try:
            run_project(self.current_project)
            self.output_panel.append_output("\n=== Program Started ===")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run project: {str(e)}")
    
    def _on_build_and_run(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please open a project first.")
            return
        
        self._on_save_all()
        
        self.output_panel.clear_output()
        self.output_panel.append_output("=== Build Started ===")
        
        self.build_thread = BuildThread(self.current_project)
        self.build_thread.build_finished.connect(self._on_build_and_run_finished)
        self.build_thread.start()
    
    def _on_build_and_run_finished(self, result: BuildResult):
        self._on_build_finished(result)
        if result.success:
            self._on_run()
    
    def _on_about(self):
        QMessageBox.about(
            self,
            "About CppLab IDE",
            "CppLab IDE v1.0\n\nA dedicated C/C++ IDE for college students\nwith support for graphics.h and OpenMP."
        )
