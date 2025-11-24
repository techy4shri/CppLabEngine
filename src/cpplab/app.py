# Main application window and UI wiring.

import os
import sys
import webbrowser
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QWidget, QPlainTextEdit, QComboBox, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal, QStandardPaths
from PyQt6.QtGui import QFont
from typing import Optional
from . import __version__
from .core.project_config import ProjectConfig, create_new_project
from .core.builder import (
    build_project, run_executable, BuildResult, get_executable_path,
    build_single_file, run_single_file
)
from .core.toolchains import get_toolchains, select_toolchain, get_app_root
from .widgets.code_editor import CodeEditor
from .widgets.project_explorer import ProjectExplorer
from .widgets.output_panel import OutputPanel
from .dialogs import NewProjectDialog
from .settings import AppSettings, load_settings, save_settings
from .settings_dialog import SettingsDialog


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
        self.standalone_files: set[Path] = set()  # Track standalone files
        self._build_and_run_mode = False  # Track if build is part of build-and-run
        
        # Load settings
        self.settings = load_settings()
        
        # Standalone settings
        self.standalone_toolchain_preference: str = "auto"
        self.standalone_standard: str = ""  # Will be set based on file type
        
        # Load UI (works in both dev and frozen modes)
        if getattr(sys, 'frozen', False):
            ui_path = get_app_root() / "cpplab" / "ui" / "MainWindow.ui"
        else:
            ui_path = Path(__file__).parent / "ui" / "MainWindow.ui"
        uic.loadUi(ui_path, self)
        
        self._setup_widgets()
        self._setup_combo_boxes()
        self._connect_signals()
        
        # Initialize toolchains and check availability
        self._check_toolchains()
        
        # Apply initial settings
        self.apply_settings()
        
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
        
        # Replace build output text with custom OutputPanel in the Build tab
        self.output_panel = OutputPanel()
        build_tab = self.outputDockWidget.findChild(QWidget, "buildTab")
        if build_tab:
            build_output_text = build_tab.findChild(QWidget, "buildOutputTextEdit")
            if build_output_text:
                build_output_text.deleteLater()
            layout = build_tab.layout()
            if layout:
                layout.addWidget(self.output_panel)
        
        # Close the placeholder tab if it exists
        if self.editorTabWidget.count() > 0:
            placeholder = self.editorTabWidget.widget(0)
            if placeholder and placeholder.objectName() == "placeholderTab":
                self.editorTabWidget.removeTab(0)
    
    def _setup_combo_boxes(self):
        """Initialize toolchain and standard combo boxes."""
        from PyQt6.QtWidgets import QLabel
        
        # Add toolchain combo to toolbar
        self.mainToolBar.addSeparator()
        toolchain_label = QLabel(" Toolchain: ")
        self.mainToolBar.addWidget(toolchain_label)
        
        self.toolchainComboBox = QComboBox()
        self.toolchainComboBox.addItem("Auto", "auto")
        self.toolchainComboBox.addItem("64-bit (mingw64)", "mingw64")
        self.toolchainComboBox.addItem("32-bit (mingw32)", "mingw32")
        self.toolchainComboBox.setMinimumWidth(150)
        self.mainToolBar.addWidget(self.toolchainComboBox)
        
        # Add standard combo to toolbar
        standard_label = QLabel(" Standard: ")
        self.mainToolBar.addWidget(standard_label)
        
        self.standardComboBox = QComboBox()
        self.standardComboBox.setMinimumWidth(100)
        self.mainToolBar.addWidget(self.standardComboBox)
        
        # Initialize with C++ standards (will be updated when files are opened)
        self._update_standard_combo_for_language("cpp", "c++17")
    
    def _update_standard_combo_for_language(self, language: str, current_standard: Optional[str] = None):
        """Update standard combo box based on language."""
        self.standardComboBox.blockSignals(True)  # Prevent triggering change event
        self.standardComboBox.clear()
        
        if language == "c":
            self.standardComboBox.addItem("C23", "c23")
            self.standardComboBox.addItem("C18", "c18")
            self.standardComboBox.addItem("C17", "c17")
            self.standardComboBox.addItem("C11", "c11")
            self.standardComboBox.addItem("C99", "c99")
            default = current_standard or "c17"
        else:  # cpp
            self.standardComboBox.addItem("C++23", "c++23")
            self.standardComboBox.addItem("C++20", "c++20")
            self.standardComboBox.addItem("C++17", "c++17")
            self.standardComboBox.addItem("C++14", "c++14")
            self.standardComboBox.addItem("C++11", "c++11")
            default = current_standard or "c++17"
        
        # Set current selection
        for i in range(self.standardComboBox.count()):
            if self.standardComboBox.itemData(i) == default:
                self.standardComboBox.setCurrentIndex(i)
                break
        
        self.standardComboBox.blockSignals(False)
    
    def _update_toolchain_combo(self, preference: str):
        """Update toolchain combo box selection."""
        self.toolchainComboBox.blockSignals(True)
        
        if preference == "auto":
            self.toolchainComboBox.setCurrentIndex(0)
        elif preference == "mingw64":
            self.toolchainComboBox.setCurrentIndex(1)
        elif preference == "mingw32":
            self.toolchainComboBox.setCurrentIndex(2)
        
        self.toolchainComboBox.blockSignals(False)
    
    def _connect_signals(self):
        # File menu
        self.newProjectAction.triggered.connect(self.on_new_project)
        self.newSourceFileAction.triggered.connect(self.on_new_source_file)
        self.openProjectAction.triggered.connect(self.on_open_project)
        self.openSourceFileAction.triggered.connect(self.on_open_source_file)
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
        
        # Combo box signals
        self.toolchainComboBox.currentIndexChanged.connect(self.on_toolchain_changed)
        self.standardComboBox.currentIndexChanged.connect(self.on_standard_changed)
    
    def on_toolchain_changed(self, index: int):
        """Handle toolchain combo box selection change."""
        # Map index to internal value
        toolchain_map = {0: "auto", 1: "mingw64", 2: "mingw32"}
        value = toolchain_map.get(index, "auto")
        
        if self.current_project:
            self.current_project.toolchain_preference = value
            self.current_project.save()
        else:
            self.standalone_toolchain_preference = value
    
    def on_standard_changed(self, index: int):
        """Handle standard combo box selection change."""
        if index < 0:
            return
        
        std_value = self.standardComboBox.currentData()
        if not std_value:
            return
        
        if self.current_project:
            self.current_project.standard = std_value
            self.current_project.save()
        else:
            self.standalone_standard = std_value
    
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
        
        # Clear standalone mode
        self.standalone_files.clear()
        
        # Update combo boxes for project
        self._update_toolchain_combo(config.toolchain_preference)
        self._update_standard_combo_for_language(config.language, config.standard)
        
        # Update status bar
        if hasattr(self, 'statusProjectLabel'):
            self.statusProjectLabel.setText(f"Project: {config.name}")
        
        self._update_ui_state()
    
    def on_new_source_file(self):
        """Create a new standalone source file."""
        # Ask user for file name and location
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "New Source File",
            str(Path.home()),
            "C Source File (*.c);;C++ Source File (*.cpp);;C++ Source File (*.cc);;C++ Source File (*.cxx);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        abs_path = Path(file_path).resolve()
        
        # Determine language from extension
        ext = abs_path.suffix.lower()
        if ext in ['.cpp', '.cc', '.cxx']:
            language = "cpp"
            template_content = """#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
        elif ext == '.c':
            language = "c"
            template_content = """#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
"""
        else:
            # Default to C++
            language = "cpp"
            template_content = """#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
        
        try:
            # Create the file with template content
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(template_content, encoding='utf-8')
            
            # Open in editor
            self.open_file_in_editor(str(abs_path))
            
            # Mark as standalone
            self.standalone_files.add(abs_path)
            
            # Clear project if this is first standalone file
            if self.current_project:
                self.current_project = None
                self.project_explorer.clear()
            
            # Update combo boxes for standalone mode
            self._update_standard_combo_for_language(language, self.standalone_standard)
            self._update_toolchain_combo(self.standalone_toolchain_preference)
            
            # Update status bar
            self.setWindowTitle(f"CppLab IDE - {abs_path.name}")
            if hasattr(self, 'statusProjectLabel'):
                self.statusProjectLabel.setText(f"Standalone: {abs_path.name}")
            
            self._update_ui_state()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create source file:\n{str(e)}")
    
    def on_open_source_file(self):
        """Open a standalone source file without creating a project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Source File",
            str(Path.home()),
            "C/C++ Source Files (*.c *.cpp *.cc *.cxx);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        abs_path = Path(file_path).resolve()
        
        # Open in editor
        self.open_file_in_editor(str(abs_path))
        
        # Mark as standalone
        self.standalone_files.add(abs_path)
        
        # Clear project if this is first standalone file
        if self.current_project:
            self.current_project = None
            self.project_explorer.clear()
        
        # Update combo boxes for standalone mode
        # Detect language from file extension
        ext = abs_path.suffix.lower()
        language = "c" if ext == ".c" else "cpp"
        self._update_standard_combo_for_language(language, self.standalone_standard)
        self._update_toolchain_combo(self.standalone_toolchain_preference)
        
        # Update status bar
        self.setWindowTitle(f"CppLab IDE - {abs_path.name}")
        if hasattr(self, 'statusProjectLabel'):
            self.statusProjectLabel.setText(f"Standalone: {abs_path.name}")
        
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
        """Build current project or standalone file."""
        # Check toolchains
        if not self.toolchains:
            QMessageBox.warning(
                self,
                "Toolchains Not Available",
                "MinGW toolchains are not installed. Please install toolchains to build."
            )
            return
        
        # Save all files before building
        self.on_save_all()
        
        # Clear output and update status
        self.output_panel.clear_output()
        self.output_panel.append_output("=== Build Started ===\n")
        
        if hasattr(self, 'statusBuildLabel'):
            self.statusBuildLabel.setText("Building...")
        
        # Determine build mode
        if self.current_project:
            # Project mode
            self.build_thread = BuildThread(self.current_project)
            if self._build_and_run_mode:
                self.build_thread.build_finished.connect(self._on_build_and_run_finished)
                self._build_and_run_mode = False
            else:
                self.build_thread.build_finished.connect(self._on_build_finished)
            self.build_thread.start()
        else:
            # Standalone mode
            editor = self.current_editor()
            if not editor or not editor.file_path:
                QMessageBox.warning(self, "No Source File", "Please open a source file to build.")
                if hasattr(self, 'statusBuildLabel'):
                    self.statusBuildLabel.setText("Idle")
                return
            
            source_path = Path(editor.file_path)
            
            # Build in background thread
            from PyQt6.QtCore import QThread
            
            class StandaloneBuildThread(QThread):
                build_finished = pyqtSignal(object)
                
                def __init__(self, path, toolchains, standard_override, toolchain_preference):
                    super().__init__()
                    self.source_path = path
                    self.toolchains = toolchains
                    self.standard_override = standard_override
                    self.toolchain_preference = toolchain_preference
                
                def run(self):
                    result = build_single_file(
                        self.source_path, 
                        self.toolchains, 
                        standard_override=self.standard_override,
                        toolchain_preference=self.toolchain_preference
                    )
                    self.build_finished.emit(result)
            
            self.build_thread = StandaloneBuildThread(
                source_path, 
                self.toolchains,
                self.standalone_standard,
                self.standalone_toolchain_preference
            )
            if self._build_and_run_mode:
                self.build_thread.build_finished.connect(self._on_build_and_run_finished)
                self._build_and_run_mode = False
            else:
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
        """Run project executable or standalone file."""
        # Check toolchains
        if not self.toolchains:
            QMessageBox.warning(
                self,
                "Toolchains Not Available",
                "MinGW toolchains are not installed. Please install toolchains to run."
            )
            return
        
        # Determine run mode
        if self.current_project:
            # Project mode
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
        else:
            # Standalone mode
            editor = self.current_editor()
            if not editor or not editor.file_path:
                QMessageBox.warning(self, "No Source File", "Please open a source file to run.")
                return
            
            source_path = Path(editor.file_path)
            
            # Check if built
            from .core.builder import project_config_for_single_file
            config = project_config_for_single_file(
                source_path, 
                standard_override=self.standalone_standard,
                toolchain_preference=self.standalone_toolchain_preference
            )
            exe_path = get_executable_path(config)
            
            if not exe_path.exists():
                reply = QMessageBox.question(
                    self,
                    "No Executable",
                    "File has not been built yet. Build now?",
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
                result = run_single_file(
                    source_path, 
                    self.toolchains,
                    standard_override=self.standalone_standard,
                    toolchain_preference=self.standalone_toolchain_preference
                )
                
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
                QMessageBox.critical(self, "Error", f"Failed to run file:\n{str(e)}")
                if hasattr(self, 'statusBuildLabel'):
                    self.statusBuildLabel.setText("Execution error")
    
    def on_build_and_run(self):
        """Build and run current project or standalone file."""
        # Just trigger build with build-and-run flag
        self._build_and_run_mode = True
        self.on_build_project()
    
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
        """Open settings dialog and apply changes if accepted."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            # Settings were modified by the dialog
            save_settings(self.settings)
            self.apply_settings()
    
    def _on_offline_docs(self):
        """Open offline documentation in default browser."""
        docs_path = get_app_root() / "docs" / "index.html"
        
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
            f"<h2>CppLab IDE v{__version__}</h2>"
            "<p>Offline C/C++ IDE with bundled MinGW 32/64, graphics.h, and OpenMP support.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Console and graphics projects</li>"
            "<li>C standards: C99, C11, C17, C18, C23</li>"
            "<li>C++ standards: C++11, C++14, C++17, C++20, C++23</li>"
            "<li>graphics.h via 32-bit MinGW with WinBGIm</li>"
            "<li>OpenMP parallel computing support</li>"
            "<li>Standalone source file mode</li>"
            "<li>Bundled MinGW toolchains</li>"
            "</ul>"
            "<p>© 2025 CppLab Project</p>"
        )
    
    # ========== UI State Management ==========
    
    def apply_settings(self):
        """Apply settings to the UI."""
        # Apply theme stylesheet
        if self.settings.theme == "sky_blue":
            stylesheet = """
            QMainWindow {
                background-color: #f0f4f8;
            }
            QMenuBar {
                background-color: #e8f0f7;
                color: #1a1a1a;
                border-bottom: 1px solid #b8d4e8;
            }
            QMenuBar::item:selected {
                background-color: #d0e4f5;
            }
            QToolBar {
                background-color: #e8f0f7;
                border: none;
                spacing: 3px;
            }
            QDockWidget {
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }
            QDockWidget::title {
                background-color: #d8e8f5;
                color: #1a1a1a;
                padding: 4px;
                border: 1px solid #b8d4e8;
            }
            QTabWidget::pane {
                border: 1px solid #b8d4e8;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e8f0f7;
                color: #1a1a1a;
                padding: 6px 12px;
                border: 1px solid #b8d4e8;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #d0e4f5;
            }
            """
            self.setStyleSheet(stylesheet)
        else:
            # Classic theme - use default styling
            self.setStyleSheet("")
        
        # Apply font settings to build output
        font = QFont("Consolas", self.settings.build_output_font_size)
        font.setBold(self.settings.build_output_bold)
        self.output_panel.setFont(font)
        
        # Store build-related settings for use in build operations
        # (accessed later in build methods)
    
    def _update_ui_state(self):
        """Update UI state based on current context."""
        has_project = self.current_project is not None
        has_editor = self.current_editor() is not None
        has_toolchains = self.toolchains is not None
        has_standalone = len(self.standalone_files) > 0 and has_editor
        
        # Can build/run if we have a project OR a standalone file
        can_build_run = (has_project or has_standalone) and has_toolchains
        
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
        
        # Build menu (works for both project and standalone)
        self.buildProjectAction.setEnabled(can_build_run)
        self.runProjectAction.setEnabled(can_build_run)
        self.buildAndRunAction.setEnabled(can_build_run)
        self.cleanProjectAction.setEnabled(has_project)  # Only for projects

