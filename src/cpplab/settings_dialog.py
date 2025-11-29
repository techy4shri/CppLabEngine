# Settings dialog for user preferences.

from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QCheckBox, QDialogButtonBox,
    QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from .settings import AppSettings


class SettingsDialog(QDialog):
    """Settings dialog with Appearance and Build tabs."""
    
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        
        self._create_ui()
        self._load_values()
    
    def _create_ui(self):
        """Create dialog UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        self.tabs.addTab(appearance_tab, "Appearance")
        
        # Build tab
        build_tab = self._create_build_tab()
        self.tabs.addTab(build_tab, "Build")
        
        # Editor tab
        editor_tab = self._create_editor_tab()
        self.tabs.addTab(editor_tab, "Editor")
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Classic Light", "classic")
        self.theme_combo.addItem("Light + Sky Blue", "sky_blue")
        theme_layout.addRow("Theme:", self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Build output group
        output_group = QGroupBox("Build Output")
        output_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 18)
        self.font_size_spin.setSuffix(" pt")
        output_layout.addRow("Font size:", self.font_size_spin)
        
        self.bold_check = QCheckBox("Bold text")
        output_layout.addRow("", self.bold_check)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
        return widget
    
    def _create_build_tab(self) -> QWidget:
        """Create build settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Build options group
        build_group = QGroupBox("Build Options")
        build_layout = QVBoxLayout()
        
        self.incremental_check = QCheckBox("Enable incremental builds")
        self.incremental_check.setToolTip(
            "Skip rebuilding if source files haven't changed"
        )
        build_layout.addWidget(self.incremental_check)
        
        self.elapsed_check = QCheckBox("Show elapsed build time in status bar")
        build_layout.addWidget(self.elapsed_check)
        
        build_group.setLayout(build_layout)
        layout.addWidget(build_group)
        
        layout.addStretch()
        return widget
    
    def _create_editor_tab(self) -> QWidget:
        """Create editor settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Indentation group
        indent_group = QGroupBox("Indentation")
        indent_layout = QFormLayout()
        
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(1, 8)
        self.tab_size_spin.setSuffix(" spaces")
        self.tab_size_spin.setToolTip("Number of spaces per tab/indent level")
        indent_layout.addRow("Tab size:", self.tab_size_spin)
        
        self.use_spaces_check = QCheckBox("Insert spaces instead of tabs")
        self.use_spaces_check.setToolTip(
            "When enabled, pressing Tab will insert spaces. "
            "When disabled, it will insert a tab character."
        )
        indent_layout.addRow("", self.use_spaces_check)
        
        self.auto_indent_check = QCheckBox("Auto-indent new lines")
        self.auto_indent_check.setToolTip(
            "Automatically match the indentation of the previous line"
        )
        indent_layout.addRow("", self.auto_indent_check)
        
        indent_group.setLayout(indent_layout)
        layout.addWidget(indent_group)
        
        layout.addStretch()
        return widget
    
    def _load_values(self):
        """Load current settings into UI controls."""
        # Appearance
        index = self.theme_combo.findData(self.settings.theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.font_size_spin.setValue(self.settings.build_output_font_size)
        self.bold_check.setChecked(self.settings.build_output_bold)
        
        # Build
        self.incremental_check.setChecked(self.settings.incremental_builds)
        self.elapsed_check.setChecked(self.settings.show_build_elapsed)
        
        # Editor
        self.tab_size_spin.setValue(self.settings.tab_size)
        self.use_spaces_check.setChecked(self.settings.use_spaces)
        self.auto_indent_check.setChecked(self.settings.auto_indent)
    
    def accept(self):
        """Save UI values to settings and close."""
        # Update settings object
        self.settings.theme = self.theme_combo.currentData()
        self.settings.build_output_font_size = self.font_size_spin.value()
        self.settings.build_output_bold = self.bold_check.isChecked()
        self.settings.incremental_builds = self.incremental_check.isChecked()
        self.settings.show_build_elapsed = self.elapsed_check.isChecked()
        self.settings.tab_size = self.tab_size_spin.value()
        self.settings.use_spaces = self.use_spaces_check.isChecked()
        self.settings.auto_indent = self.auto_indent_check.isChecked()
        
        super().accept()
