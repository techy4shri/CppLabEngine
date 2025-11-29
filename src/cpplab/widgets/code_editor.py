# Code editor widget with syntax highlighting.

import re
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt, QRegularExpression, QTimer
from typing import Optional


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_keyword = False
        self.format = None

class FastSyntaxHighlighter(QSyntaxHighlighter):
    """Using Trie (Prefix Tree) for keyword matching + Boyer-Moore for strings for faster keyword matching.
    Reduces complexity from O(n × m) (text × patterns) to O(n) + O(k) (linear scan + keyword length).
    Time to say goodbye to app lags :D
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyword_trie = self._build_keyword_trie()
        #now compiling regex once, for all
        self.string_pattern = re.compile(r'"[^"]*"|\'[^\']*\'')
        self.comment_pattern = re.compile(r'//.*$|/\*.*?\*/', re.MULTILINE)
        self.preprocessor_pattern = re.compile(r'#[^\n]*')
    
    def _build_keyword_trie(self):
        """Builds a Trie in O(total chars in keywords), query in O(length of word)."""
        root = TrieNode()
        keywords = [
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union",
            "unsigned", "void", "volatile", "while", "class", "namespace",
            "private", "protected", "public", "template", "this", "virtual",
            "bool", "true", "false", "nullptr", "using", "include", "define"
        ]
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        for word in keywords:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_keyword = True
            node.format = keyword_format
        return root
    
    def _is_word_boundary(self, text: str, pos: int) -> bool:
        """Check if position is a word boundary."""
        if pos < 0 or pos >= len(text):
            return True
        return not (text[pos].isalnum() or text[pos] == '_')
    
    def highlightBlock(self, text):
        # single pass highlight
        length = len(text)
        i = 0
        
        # Highlight keywords using Trie
        while i < length:
            # Check if we're at a word start
            if i == 0 or self._is_word_boundary(text, i - 1):
                node = self.keyword_trie
                j = i
                last_keyword_end = -1
                last_format = None
                
                # Walk the trie
                while j < length and text[j] in node.children:
                    node = node.children[text[j]]
                    j += 1
                    if node.is_keyword and self._is_word_boundary(text, j):
                        last_keyword_end = j
                        last_format = node.format
                
                # Apply format if we found a keyword
                if last_keyword_end > i and last_format:
                    self.setFormat(i, last_keyword_end - i, last_format)
                    i = last_keyword_end
                    continue
            i += 1
        
        # Highlight strings using precompiled regex
        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#008000"))
        for match in self.string_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, string_fmt)
        
        # Highlight comments using precompiled regex
        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#808080"))
        comment_fmt.setFontItalic(True)
        for match in self.comment_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, comment_fmt)
        
        # Highlight preprocessor directives
        preprocessor_fmt = QTextCharFormat()
        preprocessor_fmt.setForeground(QColor("#800080"))
        for match in self.preprocessor_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, preprocessor_fmt)

class CodeEditor(QPlainTextEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path: Optional[str] = None
        self.is_modified = False
        
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self.setTabStopDistance(40)
        
        # Use fast syntax highlighter with Trie
        self.highlighter = FastSyntaxHighlighter(self.document())
        
        # Debounced highlighting: only rehighlight after 200ms of no typing
        self.highlight_timer = QTimer()
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self._delayed_highlight)
        
        self.textChanged.connect(self._on_text_changed)
    
    def _schedule_highlight(self):
        """Schedule delayed highlight to reduce CPU during rapid typing."""
        self.highlight_timer.stop()
        self.highlight_timer.start(200)  # 200ms delay
    
    def _delayed_highlight(self):
        """Perform the actual highlighting after delay."""
        self.highlighter.rehighlight()
    
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
        # Schedule debounced highlight
        self._schedule_highlight()
