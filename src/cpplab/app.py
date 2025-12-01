# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Garima Shrivastava
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Main application window and UI wiring.

import os
import sys
import shutil
import subprocess
import webbrowser
import re
from pathlib import Path
from PyQt6 import uic
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QWidget, QPlainTextEdit, QComboBox, QLabel, QTableWidgetItem, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, QStandardPaths, Qt
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat
from typing import Optional
from . import __version__
from .core.project_config import ProjectConfig, create_new_project
from .core.builder import (
    build_project, run_executable, BuildResult, get_executable_path,
    build_single_file, run_single_file, check_project, check_single_file
)
from .core.toolchains import get_toolchains, select_toolchain, get_app_root
from .core.diagnostics import parse_gcc_output, Diagnostic
from .widgets.code_editor import CodeEditor
from .widgets.project_explorer import ProjectExplorer
from .dialogs import NewProjectDialog
from .settings import AppSettings, load_settings, save_settings
from .settings_dialog import SettingsDialog
from .ui_utils import ui_path
from functools import lru_cache
from collections import OrderedDict
import builtins
from concurrent.futures import ThreadPoolExecutor, as_completed

class EditorCache:
    """LRU cache for editor widgets with automatic eviction and dict-like API.
        Prevents memory bloat by limiting number of open editors.
        O(1) access and insertion now instead of earlier O(n) linear search"""
    def __init__(self, max_editors: int = 10):
        self._store = OrderedDict()
        self.max_editors = max_editors

    def _normalize_key(self, key):
        if isinstance(key, Path):
            return str(key.resolve())
        try:
            return str(Path(key).resolve())
        except Exception:
            return str(key)

    def __contains__(self, key):
        return self._normalize_key(key) in self._store

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def keys(self):
        return self._store.keys()

    def values(self):
        return self._store.values()

    def items(self):
        return self._store.items()

    def get(self, key, default=None):
        k = self._normalize_key(key)
        val = self._store.get(k, default)
        if val is not default:
            self._store.move_to_end(k)
        return val

    def pop(self, key, default=None):
        k = self._normalize_key(key)
        return self._store.pop(k, default)

    def clear(self):
        # will call deleteLater on Qt widgets to allow cleanup
        for editor in list(self._store.values()):
            try:
                editor.deleteLater()
            except Exception:
                pass
        self._store.clear()

    def __getitem__(self, key):
        k = self._normalize_key(key)
        val = self._store[k]
        self._store.move_to_end(k)
        return val

    def __setitem__(self, key, editor):
        k = self._normalize_key(key)
        if k in self._store:
            # replace existing and mark recently used
            self._store[k] = editor
            self._store.move_to_end(k)
            return
        # evict if needed
        if len(self._store) >= self.max_editors:
            old_path, old_editor = self._store.popitem(last=False)
            try:
                old_editor.deleteLater()
            except Exception:
                pass
        self._store[k] = editor

    def add(self, path: Path, editor: CodeEditor):
        self[path] = editor

    def popitem(self, last=True):
        return self._store.popitem(last=last)

    def move_to_end(self, key, last=True):
        k = self._normalize_key(key)
        self._store.move_to_end(k, last=last)

# Hook class creation so we can replace the per-instance open_editors dict
# with EditorCache after MainWindow is defined. This avoids modifying the
# MainWindow body across the file.
#Actually one of the best ideas I've had in a while.
_original_build_class = builtins.__build_class__

def _build_class_hook(func, name, *bases, **kwargs):
    cls = _original_build_class(func, name, *bases, **kwargs)

    if name == "MainWindow":
        # Patch __init__ to swap any plain dict assigned to self.open_editors
        # with an EditorCache, preserving any already-created editors.
        orig_init = getattr(cls, "__init__", None)

        def new_init(self, *a, **kw):
            if orig_init:
                orig_init(self, *a, **kw)

            # If the instance currently has an open_editors dict (set in __init__),
            # replace it with EditorCache while preserving contents.
            current = getattr(self, "open_editors", None)
            cache = EditorCache(max_editors=20)  # larger default for UI
            if isinstance(current, dict):
                for k, v in current.items():
                    try:
                        cache[k] = v
                    except Exception:
                        # fallback: store as-is
                        cache._store[str(k)] = v
                # replace attribute
                setattr(self, "open_editors", cache)
            elif isinstance(current, EditorCache):
                # already good
                setattr(self, "open_editors", current)
            else:
                # no existing mapping, just set a fresh cache
                setattr(self, "open_editors", cache)

        setattr(cls, "__init__", new_init)

    return cls

# Installing hook
builtins.__build_class__ = _build_class_hook

class BuildWorker(QObject):
    """Worker that runs build/check operations in a background thread."""
    
    started = pyqtSignal()
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, toolchains, project_config: Optional[ProjectConfig] = None,
                 source_path: Optional[Path] = None, force_rebuild: bool = False,
                 check_only: bool = False, toolchain_preference: str = "mingw64",
                 standard_override: Optional[str] = None, project_type: str = "console"):
        super().__init__()
        self.toolchains = toolchains
        self.project_config = project_config
        self.source_path = source_path
        self.force_rebuild = force_rebuild
        self.check_only = check_only
        self.toolchain_preference = toolchain_preference
        self.standard_override = standard_override
        self.project_type = project_type
        self._should_stop = False
    
    def stop(self):
        """Request the worker to stop."""
        self._should_stop = True
    
    @pyqtSlot()
    def run(self):
        """Execute the build/check operation."""
        try:
            self.started.emit()
            
            result = None
            if self.check_only:
                if self.project_config is not None:
                    result = check_project(self.project_config, self.toolchains)
                elif self.source_path is not None:
                    result = check_single_file(
                        self.source_path, self.toolchains, 
                        self.standard_override, self.toolchain_preference, self.project_type
                    )
            else:
                if self.project_config is not None:
                    result = build_project(self.project_config, self.toolchains, self.force_rebuild)
                elif self.source_path is not None:
                    result = build_single_file(
                        self.source_path, self.toolchains,
                        self.standard_override, self.toolchain_preference, self.project_type
                    )
            
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Build operation returned no result")
                
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    # Main application window and UI wiring.
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[ProjectConfig] = None
        self.toolchains = get_toolchains()
        self.open_editors: dict[str, CodeEditor] = {}  # file_path -> editor
        self.standalone_files: set[Path] = set()  # Track standalone files
        
        # Async build state
        self.build_in_progress = False
        self.current_build_thread: Optional[QThread] = None
        self.current_build_worker: Optional[BuildWorker] = None
        self._pending_run_after_build = False
        
        # Diagnostic counts for status bar
        self.last_error_count = 0
        self.last_warning_count = 0
        self.last_note_count = 0
        
        # Load settings
        self.settings = load_settings()
        
        # Standalone settings
        self.standalone_toolchain_preference: str = "mingw64"  # Default to 64-bit
        self.standalone_standard: str = ""  # Will be set based on file type
        self.standalone_project_type: str = "console"  # console, graphics, or openmp
        
        # Load UI (works in both dev and frozen modes)
        uic.loadUi(ui_path("MainWindow.ui"), self)
        
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
        
        # Setup problems table - connect double-click to jump to error
        self.problemsTableWidget.cellDoubleClicked.connect(self.on_problem_activated)
        self.problemsTableWidget.setColumnWidth(0, 200)  # File column
        self.problemsTableWidget.setColumnWidth(1, 50)   # Line column
        self.problemsTableWidget.setColumnWidth(2, 50)   # Column column
        self.problemsTableWidget.setColumnWidth(3, 400)  # Message column
        
        # Make table read-only (users can still select and copy text)
        self.problemsTableWidget.setEditTriggers(self.problemsTableWidget.EditTrigger.NoEditTriggers)
        
        # Add build status label to status bar
        self.statusBuildLabel = QLabel("Ready")
        self.statusbar.addPermanentWidget(self.statusBuildLabel)
        
        # Close the placeholder tab if it exists
        if self.editorTabWidget.count() > 0:
            placeholder = self.editorTabWidget.widget(0)
            if placeholder and placeholder.objectName() == "placeholderTab":
                self.editorTabWidget.removeTab(0)
    
    def _setup_combo_boxes(self):
        """Initialize toolchain and standard combo boxes."""
        
        # Add toolchain combo to toolbar
        self.mainToolBar.addSeparator()
        toolchain_label = QLabel(" Toolchain: ")
        self.mainToolBar.addWidget(toolchain_label)
        
        self.toolchainComboBox = QComboBox()
        self.toolchainComboBox.addItem("64-bit (mingw64)", "mingw64")
        self.toolchainComboBox.addItem("32-bit (mingw32)", "mingw32")
        self.toolchainComboBox.setMinimumWidth(150)
        self.mainToolBar.addWidget(self.toolchainComboBox)
        
        # Add project type combo for standalone files
        type_label = QLabel(" Type: ")
        self.mainToolBar.addWidget(type_label)
        
        self.projectTypeComboBox = QComboBox()
        self.projectTypeComboBox.addItem("Console", "console")
        self.projectTypeComboBox.addItem("Graphics", "graphics")
        self.projectTypeComboBox.addItem("OpenMP", "openmp")
        self.projectTypeComboBox.setMinimumWidth(100)
        self.projectTypeComboBox.currentIndexChanged.connect(self.on_project_type_changed)
        self.mainToolBar.addWidget(self.projectTypeComboBox)
        
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
        
        if preference == "mingw64":
            self.toolchainComboBox.setCurrentIndex(0)
        elif preference == "mingw32":
            self.toolchainComboBox.setCurrentIndex(1)
        
        self.toolchainComboBox.blockSignals(False)
    
    def on_project_type_changed(self, index: int):
        """Handle project type combo box change."""
        if self.current_project:
            return  # Ignore for project mode
        
        type_value = self.projectTypeComboBox.itemData(index)
        self.standalone_project_type = type_value
        
        # Auto-adjust toolchain based on type
        if type_value == "graphics":
            self.standalone_toolchain_preference = "mingw32"
            self._update_toolchain_combo("mingw32")
        elif type_value == "openmp":
            self.standalone_toolchain_preference = "mingw64"
            self._update_toolchain_combo("mingw64")
        # For console, keep user's choice
    
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
        self.setWindowTitle(f"CppLabEngine - {config.name}")
        
        # Clear standalone mode
        self.standalone_files.clear()
        
        # Update combo boxes for project
        self._update_toolchain_combo(config.toolchain_preference)
        self._update_standard_combo_for_language(config.language, config.standard)
        
        # Hide project type combo in project mode
        self.projectTypeComboBox.setVisible(False)
        
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
    std::cout << "Hello there! Shri this side :D" << std::endl;
    return 0;
}
"""
        elif ext == '.c':
            language = "c"
            template_content = """#include <stdio.h>

int main() {
    printf("Hello there! Shri this side :D\\n");
    return 0;
}
"""
        else:
            # Default to C++
            language = "cpp"
            template_content = """#include <iostream>

int main() {
    std::cout << "Hello there! Shri this side :D" << std::endl;
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
                # Show project type combo in standalone mode
                self.projectTypeComboBox.setVisible(True)
            
            # Update combo boxes for standalone mode
            self._update_standard_combo_for_language(language, self.standalone_standard)
            self._update_toolchain_combo(self.standalone_toolchain_preference)
            
            # Update status bar
            self.setWindowTitle(f"CppLabEngine - {abs_path.name}")
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
        self.setWindowTitle(f"CppLabEngine - {abs_path.name}")
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
            # Connect to modificationChanged signal instead of textChanged
            editor.modificationChanged.connect(lambda modified: self._on_editor_modified(editor))
            
            # Apply indentation settings
            editor.update_indentation_settings(
                self.settings.tab_size,
                self.settings.use_spaces,
                self.settings.auto_indent
            )
            
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
            # save_file() will emit modificationChanged(False) which triggers _on_editor_modified
            editor.save_file()
                
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
        if idx >= 0:
            tab_name = Path(editor.file_path).name
            current_text = self.editorTabWidget.tabText(idx)
            
            print(f"[App] _on_editor_modified: editor.is_modified={editor.is_modified}, current_text='{current_text}'")
            
            if editor.is_modified:
                # Add asterisk if not present
                if not current_text.endswith("*"):
                    print(f"[App] Adding asterisk to tab '{tab_name}'")
                    self.editorTabWidget.setTabText(idx, f"{tab_name} *")
            else:
                # Remove asterisk if present
                if current_text.endswith("*"):
                    print(f"[App] Removing asterisk from tab '{tab_name}'")
                    self.editorTabWidget.setTabText(idx, tab_name)
    
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
    
    def start_build_task(self, *, project_config: Optional[ProjectConfig] = None,
                         source_path: Optional[Path] = None, force_rebuild: bool = False,
                         check_only: bool = False) -> None:
        """Start a background build/check task if none is running."""
        if self.build_in_progress:
            reply = QMessageBox.question(
                self, "Compilation In Progress", 
                "A compilation is already running. Do you want to terminate it and start a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Terminate the current build
                if self.current_build_worker:
                    self.current_build_worker.stop()
                if self.current_build_thread:
                    self.current_build_thread.quit()
                    self.current_build_thread.wait(3000)  # Wait up to 3 seconds
                    if self.current_build_thread.isRunning():
                        self.current_build_thread.terminate()
                        self.current_build_thread.wait()
                self.build_in_progress = False
                self.current_build_thread = None
                self.current_build_worker = None
                self.statusBuildLabel.setText("Compilation terminated")
            else:
                return
        
        # Save all files before building
        if not check_only:
            self.on_save_all()
        
        # Get standalone file settings (only used if source_path is provided)
        toolchain_pref = self.standalone_toolchain_preference
        standard = self.standalone_standard if self.standalone_standard else None
        proj_type = self.standalone_project_type
        
        # Create worker and thread
        thread = QThread(self)
        worker = BuildWorker(
            toolchains=self.toolchains,
            project_config=project_config,
            source_path=source_path,
            force_rebuild=force_rebuild,
            check_only=check_only,
            toolchain_preference=toolchain_pref,
            standard_override=standard,
            project_type=proj_type
        )
        worker.moveToThread(thread)
        
        # Connect signals
        thread.started.connect(worker.run)
        worker.started.connect(self.on_build_started)
        worker.finished.connect(self.on_build_finished)
        worker.error.connect(self.on_build_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        # Store thread and worker references
        self.current_build_thread = thread
        self.current_build_worker = worker
        self.build_in_progress = True
        thread.start()
    
    @pyqtSlot()
    def on_build_started(self):
        """Handle build start - update UI to show build in progress."""
        self.statusBuildLabel.setText("Compiling...")
        self.buildProjectAction.setEnabled(True)  # Keep enabled to allow termination
        self.buildAndRunAction.setEnabled(False)
        self.runProjectAction.setEnabled(False)
        # Clear problems table at start of new build
        self.problemsTableWidget.setRowCount(0)
        self.outputDockWidget.setVisible(True)
    
    @pyqtSlot(object)
    def on_build_finished(self, result: BuildResult):
        """Handle build completion - update UI with results."""
        # Re-enable actions
        self.buildProjectAction.setEnabled(True)
        self.buildAndRunAction.setEnabled(True)
        self.runProjectAction.setEnabled(True)
        self.build_in_progress = False
        self.current_build_thread = None
        self.current_build_worker = None
        
        # Parse and display diagnostics in Problems table (sets counts)
        self.update_problems_from_result(result)
        
        # Build status message with error/warning counts
        if result.skipped:
            msg = "Compilation skipped (up to date)"
        else:
            msg = "Compilation succeeded" if result.success else "Compilation failed"
            
            # Add elapsed time if enabled
            if hasattr(result, "elapsed_ms") and self.settings.show_build_elapsed and result.elapsed_ms > 0:
                msg += f" in {result.elapsed_ms:.0f} ms"
            
            # Add error and warning counts
            errors = getattr(self, "last_error_count", 0)
            warnings = getattr(self, "last_warning_count", 0)
            
            msg += f" ({errors} error{'s' if errors != 1 else ''}"
            msg += f", {warnings} warning{'s' if warnings != 1 else ''})"
        
        self.statusBuildLabel.setText(msg)
        
        # Handle pending run after build
        if result.success and self._pending_run_after_build:
            self._pending_run_after_build = False
            self.run_current()
    
    @pyqtSlot(str)
    def on_build_error(self, message: str):
        """Handle build error."""
        self.build_in_progress = False
        self.current_build_thread = None
        self.current_build_worker = None
        self.buildProjectAction.setEnabled(True)
        self.buildAndRunAction.setEnabled(True)
        self.runProjectAction.setEnabled(True)
        self.statusBuildLabel.setText("Compilation error")
        QMessageBox.critical(self, "Compilation Error", message)
    
    def clear_error_highlights(self) -> None:
        """Clear any error highlights in all open editors."""
        for i in range(self.editorTabWidget.count()):
            widget = self.editorTabWidget.widget(i)
            if isinstance(widget, CodeEditor):
                # Clear error selections by setting empty list
                if not hasattr(widget, 'errorSelections'):
                    widget.errorSelections = []
                widget.errorSelections = []
                widget.setExtraSelections([])
    
    def update_problems_from_result(self, result: BuildResult) -> None:
        """Fill the Problems table and highlight lines based on build stderr."""
        # Clear existing problems
        self.problemsTableWidget.setRowCount(0)
        
        # Clear previous error highlights
        self.clear_error_highlights()
        
        # Reset counts
        self.last_error_count = 0
        self.last_warning_count = 0
        self.last_note_count = 0
        
        if not result.stderr:
            return
        
        # Parse diagnostics from stderr
        diagnostics = parse_gcc_output(result.stderr)
        
        if not diagnostics:
            return
        
        # Compute counts by severity
        self.last_error_count = sum(1 for d in diagnostics if d.severity == "error")
        self.last_warning_count = sum(1 for d in diagnostics if d.severity == "warning")
        self.last_note_count = sum(1 for d in diagnostics if d.severity == "note")
        
        # Set table row count
        self.problemsTableWidget.setRowCount(len(diagnostics))
        
        # Populate table with diagnostics
        for i, diag in enumerate(diagnostics):
            # Column 0: File (basename for display, full path in UserRole)
            file_item = QTableWidgetItem(diag.file.name)
            file_item.setData(Qt.ItemDataRole.UserRole, str(diag.file))
            
            # Column 1: Line
            line_item = QTableWidgetItem(str(diag.line))
            
            # Column 2: Column
            col_item = QTableWidgetItem(str(diag.column))
            
            # Column 3: Message with severity prefix
            msg_item = QTableWidgetItem(f"[{diag.severity}] {diag.message}")
            
            # Determine color by severity
            color = None
            if diag.severity == 'error':
                color = QColor(200, 0, 0)  # Red
            elif diag.severity == 'warning':
                color = QColor(180, 120, 0)  # Dark orange/yellow
            elif diag.severity == 'note':
                color = QColor(100, 100, 100)  # Grey
            
            # Apply color to all columns in the row
            for col, item in enumerate([file_item, line_item, col_item, msg_item]):
                if color is not None:
                    item.setForeground(color)
                self.problemsTableWidget.setItem(i, col, item)
            
            # Highlight diagnostic in editor if file is open
            self.highlight_diagnostic_in_editor(diag)
        
        # Show problems dock if we have diagnostics
        if diagnostics:
            self.outputDockWidget.setVisible(True)
    
    def highlight_diagnostic_in_editor(self, diag: Diagnostic) -> None:
        """If the file is open, highlight the diagnostic line in the editor."""
        # Find editor for this file
        editor = self.find_editor_for_path(diag.file)
        
        if not editor:
            return  # File not open, do nothing
        
        # Get the block (line) for this diagnostic
        doc = editor.document()
        block = doc.findBlockByNumber(diag.line - 1)  # 0-based
        
        if not block.isValid():
            return
        
        cursor = QTextCursor(block)
        
        # Create extra selection for error highlighting
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor(255, 220, 220))  # Light red
        selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
        
        # Store error selections on editor
        if not hasattr(editor, 'errorSelections'):
            editor.errorSelections = []
        editor.errorSelections.append(selection)
        
        # Apply all error selections
        editor.setExtraSelections(editor.errorSelections)
    
    def find_editor_for_path(self, file_path: Path) -> Optional[CodeEditor]:
        """Find an open editor for the given file path."""
        # Normalize path for comparison
        target_path = str(file_path.resolve()) if file_path.is_absolute() else str(file_path)
        
        for i in range(self.editorTabWidget.count()):
            widget = self.editorTabWidget.widget(i)
            if isinstance(widget, CodeEditor) and widget.file_path:
                editor_path = str(Path(widget.file_path).resolve())
                if editor_path == target_path or widget.file_path == target_path:
                    return widget
        
        return None
    
    def on_problem_activated(self, row: int, column: int) -> None:
        """Open the file and jump to the diagnostic line when a problem is double-clicked."""
        # Get items from table
        file_item = self.problemsTableWidget.item(row, 0)
        line_item = self.problemsTableWidget.item(row, 1)
        col_item = self.problemsTableWidget.item(row, 2)
        
        if not file_item:
            return
        
        # Retrieve full path from UserRole
        path_str = file_item.data(Qt.ItemDataRole.UserRole) or file_item.text()
        file_path = Path(path_str)
        
        # Parse line/column
        try:
            line = int(line_item.text()) if line_item else 1
        except ValueError:
            line = 1
        
        try:
            col = int(col_item.text()) if col_item else 1
        except ValueError:
            col = 1
        
        # Resolve relative paths
        if not file_path.is_absolute():
            if self.current_project:
                file_path = self.current_project.root_path / file_path
            else:
                current_editor = self.current_editor()
                if current_editor and current_editor.file_path:
                    file_path = Path(current_editor.file_path).parent / file_path
        
        # Open file if not already open
        editor = self.find_editor_for_path(file_path)
        
        if not editor and file_path.exists():
            # Open the file in a new tab
            try:
                editor = CodeEditor()
                editor.load_file(str(file_path))
                
                # Apply indentation settings
                editor.update_indentation_settings(
                    self.settings.tab_size,
                    self.settings.use_spaces,
                    self.settings.auto_indent
                )
                
                tab_name = file_path.name
                self.editorTabWidget.addTab(editor, tab_name)
                self.editorTabWidget.setCurrentWidget(editor)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file:\n{e}")
                return
        elif editor:
            # Switch to existing tab
            for i in range(self.editorTabWidget.count()):
                if self.editorTabWidget.widget(i) == editor:
                    self.editorTabWidget.setCurrentIndex(i)
                    break
        
        if not editor:
            return
        
        # Move cursor to diagnostic location
        doc = editor.document()
        block = doc.findBlockByNumber(line - 1)  # 0-based
        
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.setPosition(block.position() + max(col - 1, 0))
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()
            
            # Refresh error highlight for this line
            selection = QTextEdit.ExtraSelection()
            selection.cursor = QTextCursor(block)
            selection.format.setBackground(QColor(255, 220, 220))
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            
            if not hasattr(editor, 'errorSelections'):
                editor.errorSelections = []
            
            # Check if this line already has a highlight to avoid duplicates
            has_highlight = False
            for sel in editor.errorSelections:
                if sel.cursor.blockNumber() == block.blockNumber():
                    has_highlight = True
                    break
            
            if not has_highlight:
                editor.errorSelections.append(selection)
                editor.setExtraSelections(editor.errorSelections)
    
    def build_current(self, force_rebuild: bool = False, check_only: bool = False):
        """Build current project or standalone file."""
        if self.current_project is not None:
            self.start_build_task(
                project_config=self.current_project,
                force_rebuild=force_rebuild,
                check_only=check_only
            )
        else:
            # Standalone file mode
            editor = self.current_editor()
            if not editor or not editor.file_path:
                QMessageBox.warning(self, "No Source File", 
                                   "Please open a source file to build.")
                return
            
            self.start_build_task(
                source_path=Path(editor.file_path),
                force_rebuild=force_rebuild,
                check_only=check_only
            )
    
    def run_current(self):
        """Run current project or standalone file executable in external terminal."""
        if self.current_project:
            exe_path = get_executable_path(self.current_project)
            if not exe_path.exists():
                reply = QMessageBox.question(
                    self, "No Executable",
                    "Project has not been compiled yet. Compile now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._pending_run_after_build = True
                    self.build_current()
                return
            
            # Always launch in external terminal (all project types)
            self.statusBuildLabel.setText("Running...")
            try:
                # Use 'start' command on Windows to open in new terminal
                subprocess.Popen(f'start cmd /k "{exe_path}"', shell=True)
                self.statusBuildLabel.setText("Program started in terminal")
            except Exception as e:
                QMessageBox.warning(self, "Launch Error", f"Failed to launch terminal: {e}")
                self.statusBuildLabel.setText("Failed to launch")
        else:
            # Standalone file
            editor = self.current_editor()
            if not editor or not editor.file_path:
                return
            
            source_path = Path(editor.file_path)
            # For standalone files, executable is directly in source directory
            exe_path = source_path.parent / f"{source_path.stem}.exe"
            
            if not exe_path.exists():
                reply = QMessageBox.question(
                    self, "No Executable",
                    "File has not been compiled yet. Compile now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._pending_run_after_build = True
                    self.build_current()
                return
            
            # Always launch in external terminal (all file types: console, graphics, openmp)
            self.statusBuildLabel.setText("Running...")
            try:
                # Use 'start' command on Windows to open in new terminal
                subprocess.Popen(f'start cmd /k "{exe_path}"', shell=True)
                self.statusBuildLabel.setText("Program started in terminal")
            except Exception as e:
                QMessageBox.warning(self, "Launch Error", f"Failed to launch terminal: {e}")
                self.statusBuildLabel.setText("Failed to launch")
    
    def on_build_project(self):
        """Build current project or standalone file."""
        if not self.toolchains:
            QMessageBox.warning(self, "Toolchains Not Available",
                              "MinGW toolchains are not installed. Please install toolchains to build.")
            return
        self.build_current()
    
    def on_run_project(self):
        """Run project executable or standalone file."""
        if not self.toolchains:
            QMessageBox.warning(self, "Toolchains Not Available",
                              "MinGW toolchains are not installed. Please install toolchains to run.")
            return
        self.run_current()
    
    def on_build_and_run(self):
        """Build and run current project or standalone file."""
        if not self.toolchains:
            QMessageBox.warning(self, "Toolchains Not Available",
                              "MinGW toolchains are not installed. Please install toolchains.")
            return
        self._pending_run_after_build = True
        self.build_current()
    
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
            shutil.rmtree(build_dir)
            build_dir.mkdir()
            
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
        """Show about dialog with GitHub wiki link."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About CppLabEngine")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(
            f"<h2>CppLabEngine v{__version__}</h2>"
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
            "<p>© 2025 Garima Shrivastava</p>"
            '<p><a href="https://github.com/techy4shri/CppLabEngine/wiki">Visit Documentation Wiki</a></p>'
        )
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
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
        
        # Apply indentation settings to all open editors
        for editor in self.open_editors.values():
            editor.update_indentation_settings(
                self.settings.tab_size,
                self.settings.use_spaces,
                self.settings.auto_indent
            )
        
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
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.build_in_progress:
            reply = QMessageBox.question(
                self, "Compilation in progress",
                "A compilation is currently running. Do you really want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # Terminate the build thread gracefully
            if self.current_build_worker:
                self.current_build_worker.stop()
            if self.current_build_thread:
                self.current_build_thread.quit()
                self.current_build_thread.wait(2000)  # Wait up to 2 seconds
                if self.current_build_thread.isRunning():
                    self.current_build_thread.terminate()
                    self.current_build_thread.wait()
        
        event.accept()
        super().closeEvent(event)

def build_project_parallel(config: ProjectConfig, toolchains, max_workers=4):
    """Compile multiple source files in parallel."""
    
    # Group files by independence (files without shared headers)
    independent_files = _partition_by_dependencies(config.files)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_group in independent_files:
            # Submit compilation tasks
            future = executor.submit(_compile_group, file_group, config, toolchains)
            futures.append(future)
        
        # Collect results as they complete
        for future in as_completed(futures):
            result = future.result()
            if not result.success:
                return result  # Early exit on error
    
    # Link phase (sequential, required)
    return _link_objects(config)
