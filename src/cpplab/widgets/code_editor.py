# Code editor widget with syntax highlighting.

from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt, QRegularExpression
from typing import Optional


class CppSyntaxHighlighter(QSyntaxHighlighter):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_rules()
    
    def _setup_rules(self):
        self.highlighting_rules = []
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union",
            "unsigned", "void", "volatile", "while", "class", "namespace",
            "private", "protected", "public", "template", "this", "virtual",
            "bool", "true", "false", "nullptr", "using", "include", "define"
        ]
        
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append((QRegularExpression('".*?"'), string_format))
        self.highlighting_rules.append((QRegularExpression("'.*?'"), string_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("//[^\n]*"), comment_format))
        
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor("#800080"))
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), preprocessor_format))
    
    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class CodeEditor(QPlainTextEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path: Optional[str] = None
        self.is_modified = False
        
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self.setTabStopDistance(40)
        
        self.highlighter = CppSyntaxHighlighter(self.document())
        
        self.textChanged.connect(self._on_text_changed)
    
    def load_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.setPlainText(content)
        self.file_path = file_path
        self.is_modified = False
    
    def save_file(self):
        if not self.file_path:
            return
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.toPlainText())
        self.is_modified = False
    
    def _on_text_changed(self):
        if self.file_path:
            self.is_modified = True
