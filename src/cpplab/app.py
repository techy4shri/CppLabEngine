# Main application window and UI wiring.

import os
import webbrowser
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QWidget, QPlainTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal, QStandardPaths
from typing import Optional
from .core.project_config import ProjectConfig, create_new_project
from .core.builder import build_project, run_executable, BuildResult, get_executable_path
from .core.toolchains import get_toolchains
from .widgets.code_editor import CodeEditor
from .widgets.project_explorer import ProjectExplorer
from .widgets.output_panel import OutputPanel
from .dialogs import NewProjectDialog


class BuildThread(QThread):
    
    build_finished = pyqtSignal(object)
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
    
    def run(self):
        result = build_project(self.project_config, get_toolchains())
        self.build_finished.emit(result)


class MainWindow(QMainWindow):
    # Main application window and UI wiring.
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[ProjectConfig] = None
        self.toolchains = get_toolchains()
        self.build_thread: Optional[BuildThread] = None
        self.open_editors: dict[str, CodeEditor] = {}  # file_path -> editor
        
        # Load UI
        ui_path = Path(__file__).parent / "ui" / "MainWindow.ui"
        uic.loadUi(ui_path, self)
        
        self._setup_widgets()
        self._connect_signals()
        
        # Initialize toolchains and check availability
        self._check_toolchains()
        
        self._update_ui_state()
    
    def _setup_widgets(self):
        # Replace project tree view with custom ProjectExplorer
        self.project_explorer = ProjectExplorer()
        project_dock_content = self.projectDockWidget.findChild(QWidget, "projectDockContent")
        if project_dock_content:
            project_tree_view = project_dock_content.findChild(QWidget, "projectTreeView")
            if project_tree_view:
                project_tree_view.deleteLater()
            layout = project_dock_content.layout()
            if layout:
                layout.addWidget(self.project_explorer)
        
        # Replace build output text with custom OutputPanel
        self.output_panel = OutputPanel()
        output_dock_content = self.outputDockWidget.findChild(QWidget, "outputDockContent")
        if output_dock_content:
            build_output_text = output_dock_content.findChild(QWidget, "buildOutputTextEdit")
            if build_output_text:
                build_output_text.deleteLater()
            layout = output_dock_content.layout()
            if layout:
                layout.addWidget(self.output_panel)
        
        # Close the placeholder tab if it exists
        if self.editorTabWidget.count() > 0:
            placeholder = self.editorTabWidget.widget(0)
            if placeholder and placeholder.objectName() == "placeholderTab":
                self.editorTabWidget.removeTab(0)
    
    def _connect_signals(self):
        # File menu
        self.newProjectAction.triggered.connect(self.on_new_project)
        self.openProjectAction.triggered.connect(self.on_open_project)
        self.saveFileAction.triggered.connect(self.on_save_file)
        self.saveAllAction.triggered.connect(self.on_save_all)
        self.closeFileAction.triggered.connect(self.on_close_file)
        self.exitAction.triggered.connect(self.close)
        
        # Edit menu - wire to current editor
        self.undoAction.triggered.connect(self._on_undo)
        self.redoAction.triggered.connect(self._on_redo)
        self.cutAction.triggered.connect(self._on_cut)
        self.copyAction.triggered.connect(self._on_copy)
        self.pasteAction.triggered.connect(self._on_paste)
        self.findAction.triggered.connect(self._on_find)
        self.replaceAction.triggered.connect(self._on_replace)
        
        # View menu - toggle docks
        self.viewProjectDockAction.triggered.connect(
            lambda: self.projectDockWidget.setVisible(not self.projectDockWidget.isVisible())
        )
        self.viewOutputDockAction.triggered.connect(
            lambda: self.outputDockWidget.setVisible(not self.outputDockWidget.isVisible())
        )
        self.viewProblemsDockAction.triggered.connect(
            lambda: self.problemsDockWidget.setVisible(not self.problemsDockWidget.isVisible())
        )
        
        # Build menu
        self.buildProjectAction.triggered.connect(self.on_build_project)
        self.runProjectAction.triggered.connect(self.on_run_project)
        self.buildAndRunAction.triggered.connect(self.on_build_and_run)
        self.cleanProjectAction.triggered.connect(self.on_clean_project)
        
        # Tools menu
        self.settingsAction.triggered.connect(self._on_settings)
        
        # Help menu
        self.offlineDocsAction.triggered.connect(self._on_offline_docs)
        self.aboutAction.triggered.connect(self._on_about)
        
        # Widget signals
        self.project_explorer.file_double_clicked.connect(self.open_file_in_editor)
        self.editorTabWidget.tabCloseRequested.connect(self._close_editor_tab)
        self.editorTabWidget.currentChanged.connect(self._on_tab_changed)
    
    def _check_toolchains(self):
        """Check if toolchains are available and show warning if not."""
        try:
            self.toolchains = get_toolchains()
            
            mingw32 = self.toolchains.get("mingw32")
            mingw64 = self.toolchains.get("mingw64")
            
            missing = []
            if not mingw32 or not mingw32.is_available():
                missing.append("mingw32 (32-bit, required for graphics.h)")
            if not mingw64 or not mingw64.is_available():
                missing.append("mingw64 (64-bit, required for OpenMP)")
            
            if missing:
                from .core.toolchains import get_app_root
                app_root = get_app_root()
                
                msg = (
                    "<h3>Toolchains Not Found</h3>"
                    "<p>The following MinGW toolchains are missing:</p>"
                    "<ul>"
                )
                for item in missing:
                    msg += f"<li>{item}</li>"
                msg += "</ul>"
                msg += (
                    f"<p><b>Expected location:</b><br>"
                    f"<code>{app_root / 'compilers'}</code></p>"
                    "<p><b>Setup instructions:</b></p>"
                    "<ol>"
                    "<li>Download MinGW 32-bit and 64-bit distributions</li>"
                    "<li>Extract to <code>compilers/mingw32</code> and <code>compilers/mingw64</code></li>"
                    "<li>Ensure graphics.h libraries are in mingw32</li>"
                    "<li>Restart the IDE</li>"
                    "</ol>"
                    "<p>Build and run features will be disabled until toolchains are installed.</p>"
                )
                
                QMessageBox.warning(
                    self,
                    "Toolchains Missing",
                    msg
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to initialize toolchains:\n{str(e)}"
            )
    
    # ========== Project Management ==========
    
    def set_current_project(self, config: ProjectConfig):
        """Load project and update UI."""
        self.current_project = config
        self.project_explorer.load_project(config)
        self.setWindowTitle(f"CppLab IDE - {config.name}")
        
        # Update status bar
        if hasattr(self, 'statusProjectLabel'):
            self.statusProjectLabel.setText(f"Project: {config.name}")
        
        self._update_ui_state()
    
    def on_new_project(self):
        """Show new project dialog and create project."""
        dialog = NewProjectDialog(self)
        if dialog.exec():
            project_data = dialog.get_project_data()
            
            # Validate input
            if not project_data["name"]:
                QMessageBox.warning(self, "Invalid Input", "Project name cannot be empty.")
                return
            
            try:
                project = create_new_project(**project_data)
                self.set_current_project(project)
                
                # Open main file in editor
                main_file_path = project.get_main_file_path()
                self.open_file_in_editor(str(main_file_path))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project:\n{str(e)}")
    
    def on_open_project(self):
        """Open existing project from directory."""
        project_dir = QFileDialog.getExistingDirectory(
            self, 
            "Open Project",
            str(Path.home())
        )
        
        if not project_dir:
            return
        
        config_file = Path(project_dir) / ".cpplab.json"
        if not config_file.exists():
            QMessageBox.warning(
                self, 
                "Invalid Project", 
                "The selected directory is not a valid CppLab project.\n"
                "Missing .cpplab.json configuration file."
            )
            return
        
        try:
            project = ProjectConfig.load(project_dir)
            self.set_current_project(project)
            
            # Open main file in editor if it exists
            main_file_path = project.get_main_file_path()
            if main_file_path.exists():
                self.open_file_in_editor(str(main_file_path))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project:\n{str(e)}")
    
    # ========== Editor Tab Management ==========
    
    def open_file_in_editor(self, file_path: str):
        """Open file in editor tab, or activate existing tab."""
        abs_path = str(Path(file_path).resolve())
        
        # Check if already open
        if abs_path in self.open_editors:
            editor = self.open_editors[abs_path]
            idx = self.editorTabWidget.indexOf(editor)
            if idx >= 0:
                self.editorTabWidget.setCurrentIndex(idx)
                return
        
        # Create new editor
        try:
            editor = CodeEditor()
            editor.load_file(abs_path)
            editor.textChanged.connect(lambda: self._on_editor_modified(editor))
            
            tab_name = Path(abs_path).name
            idx = self.editorTabWidget.addTab(editor, tab_name)
            self.editorTabWidget.setCurrentIndex(idx)
            
            self.open_editors[abs_path] = editor
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
    
    def current_editor(self) -> Optional[CodeEditor]:
        """Return currently active editor widget."""
        widget = self.editorTabWidget.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None
    
    def current_file_path(self) -> Optional[Path]:
        """Return path of currently active file."""
        editor = self.current_editor()
        if editor and editor.file_path:
            return Path(editor.file_path)
        return None
    
    def save_editor(self, editor: CodeEditor):
        """Save editor contents to disk."""
        if not editor or not editor.file_path:
            return
        
        try:
            editor.save_file()
            
            # Update tab title to remove dirty marker
            idx = self.editorTabWidget.indexOf(editor)
            if idx >= 0:
                tab_name = Path(editor.file_path).name
                self.editorTabWidget.setTabText(idx, tab_name)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def _close_editor_tab(self, index: int):
        """Close editor tab with save prompt if modified."""
        editor = self.editorTabWidget.widget(index)
        
        if isinstance(editor, CodeEditor) and editor.is_modified:
            file_name = Path(editor.file_path).name if editor.file_path else "Untitled"
            
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                f"Save changes to {file_name}?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_editor(editor)
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Remove from tracking
        if isinstance(editor, CodeEditor) and editor.file_path:
            abs_path = str(Path(editor.file_path).resolve())
            self.open_editors.pop(abs_path, None)
        
        self.editorTabWidget.removeTab(index)
    
    def _on_editor_modified(self, editor: CodeEditor):
        """Mark tab as modified when editor text changes."""
        if not editor.file_path:
            return
        
        idx = self.editorTabWidget.indexOf(editor)
        if idx >= 0 and editor.is_modified:
            tab_name = Path(editor.file_path).name
            if not self.editorTabWidget.tabText(idx).endswith("*"):
                self.editorTabWidget.setTabText(idx, f"{tab_name} *")
    
    def _on_tab_changed(self, index: int):
        """Update UI state when active tab changes."""
        self._update_ui_state()
    
    # ========== File Menu Actions ==========
    
    def on_save_file(self):
        """Save current editor file."""
        editor = self.current_editor()
        if editor:
            self.save_editor(editor)
        else:
            QMessageBox.information(self, "No File", "No file is currently open.")
    
    def on_save_all(self):
        """Save all open editor files."""
        for editor in self.open_editors.values():
            if editor.is_modified:
                self.save_editor(editor)
    
    def on_close_file(self):
        """Close current editor tab."""
        current_idx = self.editorTabWidget.currentIndex()
        if current_idx >= 0:
            self._close_editor_tab(current_idx)
    
    # ========== Edit Menu Actions ==========
    
    def _on_undo(self):
        editor = self.current_editor()
        if editor:
            editor.undo()
    
    def _on_redo(self):
        editor = self.current_editor()
        if editor:
            editor.redo()
    
    def _on_cut(self):
        editor = self.current_editor()
        if editor:
            editor.cut()
    
    def _on_copy(self):
        editor = self.current_editor()
        if editor:
            editor.copy()
    
    def _on_paste(self):
        editor = self.current_editor()
        if editor:
            editor.paste()
    
    def _on_find(self):
        # TODO: Implement find dialog
        QMessageBox.information(self, "Find", "Find dialog not yet implemented.")
    
    def _on_replace(self):
        # TODO: Implement replace dialog
        QMessageBox.information(self, "Replace", "Replace dialog not yet implemented.")
    
    # ========== Build & Run Integration ==========
    
    def append_build_output(self, text: str):
        """Append text to build output panel."""
        self.output_panel.append_output(text)
    
    def on_build_project(self):
        """Build current project."""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        # Check toolchains
        if not self.toolchains:
            QMessageBox.warning(
                self,
                "Toolchains Not Available",
                "MinGW toolchains are not installed. Please install toolchains to build projects."
            )
            return
        
        # Save all files before building
        self.on_save_all()
        
        # Clear output and update status
        self.output_panel.clear_output()
        self.output_panel.append_output("=== Build Started ===\n")
        
        if hasattr(self, 'statusBuildLabel'):
            self.statusBuildLabel.setText("Building...")
        
        # Start build in background thread
        self.build_thread = BuildThread(self.current_project)
        self.build_thread.build_finished.connect(self._on_build_finished)
        self.build_thread.start()
    
    def _on_build_finished(self, result: BuildResult):
        """Handle build completion."""
        self.output_panel.append_output(f"\nCommand: {' '.join(result.command)}\n")
        
        if result.stdout:
            self.output_panel.append_output("\n--- Standard Output ---\n")
            self.output_panel.append_output(result.stdout)
        
        if result.stderr:
            self.output_panel.append_output("\n--- Standard Error ---\n")
            self.output_panel.append_output(result.stderr)
        
        if result.success:
            self.output_panel.append_output("\n=== Build Succeeded ===")
            if hasattr(self, 'statusBuildLabel'):
                self.statusBuildLabel.setText("Build succeeded")
            
            # Clear problems table
            if hasattr(self, 'problemsTableWidget'):
                self.problemsTableWidget.setRowCount(0)
        else:
            self.output_panel.append_output("\n=== Build Failed ===")
            if hasattr(self, 'statusBuildLabel'):
                self.statusBuildLabel.setText("Build failed")
            
            # TODO: Parse stderr into problems table
            # For v1, just leave it empty or add a single row
    
    def on_run_project(self):
        """Run project executable."""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        # Check toolchains
        if not self.toolchains:
            QMessageBox.warning(
                self,
                "Toolchains Not Available",
                "MinGW toolchains are not installed. Please install toolchains to run projects."
            )
            return
        
        # Check if executable exists
        exe_path = get_executable_path(self.current_project)
        if not exe_path.exists():
            reply = QMessageBox.question(
                self,
                "No Executable",
                "Project has not been built yet. Build now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.on_build_and_run()
            return
        
        # Run executable
        if hasattr(self, 'statusBuildLabel'):
            self.statusBuildLabel.setText("Running...")
        
        self.output_panel.append_output("\n=== Running Executable ===\n")
        
        try:
            result = run_executable(self.current_project, self.toolchains)
            
            self.output_panel.append_output(f"Command: {' '.join(result.command)}\n")
            
            if result.stdout:
                self.output_panel.append_output("\n--- Program Output ---\n")
                self.output_panel.append_output(result.stdout)
            
            if result.stderr:
                self.output_panel.append_output("\n--- Error Output ---\n")
                self.output_panel.append_output(result.stderr)
            
            if result.success:
                self.output_panel.append_output("\n=== Execution Completed ===")
                if hasattr(self, 'statusBuildLabel'):
                    self.statusBuildLabel.setText("Execution completed")
            else:
                self.output_panel.append_output("\n=== Execution Failed ===")
                if hasattr(self, 'statusBuildLabel'):
                    self.statusBuildLabel.setText("Execution failed")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run project:\n{str(e)}")
            if hasattr(self, 'statusBuildLabel'):
                self.statusBuildLabel.setText("Execution error")
    
    def on_build_and_run(self):
        """Build project and run if successful."""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        # Check toolchains
        if not self.toolchains:
            QMessageBox.warning(
                self,
                "Toolchains Not Available",
                "MinGW toolchains are not installed. Please install toolchains to build and run projects."
            )
            return
        
        # Save all files before building
        self.on_save_all()
        
        # Clear output and update status
        self.output_panel.clear_output()
        self.output_panel.append_output("=== Build Started ===\n")
        
        if hasattr(self, 'statusBuildLabel'):
            self.statusBuildLabel.setText("Building...")
        
        # Start build in background thread
        self.build_thread = BuildThread(self.current_project)
        self.build_thread.build_finished.connect(self._on_build_and_run_finished)
        self.build_thread.start()
    
    def _on_build_and_run_finished(self, result: BuildResult):
        """Handle build completion and run if successful."""
        self._on_build_finished(result)
        
        if result.success:
            self.on_run_project()
    
    def on_clean_project(self):
        """Clean project build directory."""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        build_dir = self.current_project.root_path / "build"
        
        if not build_dir.exists():
            QMessageBox.information(self, "Clean", "Build directory is already clean.")
            return
        
        try:
            import shutil
            shutil.rmtree(build_dir)
            build_dir.mkdir()
            
            self.output_panel.clear_output()
            self.output_panel.append_output("=== Clean Completed ===\n")
            self.output_panel.append_output(f"Removed build directory: {build_dir}")
            
            if hasattr(self, 'statusBuildLabel'):
                self.statusBuildLabel.setText("Clean completed")
            
            QMessageBox.information(self, "Clean", "Build directory cleaned successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clean build directory:\n{str(e)}")
    
    # ========== Tools & Help Menu Actions ==========
    
    def _on_settings(self):
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")
    
    def _on_offline_docs(self):
        """Open offline documentation in default browser."""
        docs_path = Path(__file__).parent.parent.parent / "docs" / "index.html"
        
        if docs_path.exists():
            webbrowser.open(docs_path.as_uri())
        else:
            QMessageBox.warning(
                self,
                "Documentation Not Found",
                f"Offline documentation not found at:\n{docs_path}"
            )
    
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CppLab IDE",
            "<h2>CppLab IDE v1.0</h2>"
            "<p>A dedicated offline C/C++ IDE for college students</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Support for graphics.h (32-bit legacy graphics)</li>"
            "<li>Support for OpenMP (parallel computing)</li>"
            "<li>Bundled MinGW toolchains</li>"
            "<li>Project-based workflow</li>"
            "</ul>"
            "<p>© 2025 CppLab Project</p>"
        )
    
    # ========== UI State Management ==========
    
    def _update_ui_state(self):
        """Update UI state based on current context."""
        has_project = self.current_project is not None
        has_editor = self.current_editor() is not None
        has_toolchains = self.toolchains is not None
        
        # File menu
        self.saveFileAction.setEnabled(has_editor)
        self.saveAllAction.setEnabled(has_editor)
        self.closeFileAction.setEnabled(has_editor)
        
        # Edit menu
        self.undoAction.setEnabled(has_editor)
        self.redoAction.setEnabled(has_editor)
        self.cutAction.setEnabled(has_editor)
        self.copyAction.setEnabled(has_editor)
        self.pasteAction.setEnabled(has_editor)
        self.findAction.setEnabled(has_editor)
        self.replaceAction.setEnabled(has_editor)
        
        # Build menu (requires both project and toolchains)
        self.buildProjectAction.setEnabled(has_project and has_toolchains)
        self.runProjectAction.setEnabled(has_project and has_toolchains)
        self.buildAndRunAction.setEnabled(has_project and has_toolchains)
        self.cleanProjectAction.setEnabled(has_project)
