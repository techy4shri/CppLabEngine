# Output panel for displaying build messages.

from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QTextCursor


class OutputPanel(QPlainTextEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
    
    def append_output(self, text: str):
        self.appendPlainText(text)
        self.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear_output(self):
        self.clear()
