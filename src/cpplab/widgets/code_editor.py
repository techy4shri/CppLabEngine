# Code editor widget with syntax highlighting.

import re
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor
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
        
        # Indentation settings (defaults, will be updated by app)
        self.tab_size = 4
        self.use_spaces = True
        self.auto_indent = True
        
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self._update_tab_stop_distance()
        
        # Use fast syntax highlighter with Trie
        self.highlighter = FastSyntaxHighlighter(self.document())
        
        # Debounced highlighting: only rehighlight after 200ms of no typing
        self.highlight_timer = QTimer()
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self._delayed_highlight)
        
        self.textChanged.connect(self._on_text_changed)
    
    def _update_tab_stop_distance(self):
        """Update tab stop distance based on tab size setting."""
        # Get the width of a space character
        font_metrics = self.fontMetrics()
        space_width = font_metrics.horizontalAdvance(' ')
        self.setTabStopDistance(space_width * self.tab_size)
    
    def update_indentation_settings(self, tab_size: int, use_spaces: bool, auto_indent: bool):
        """Update indentation settings from app settings."""
        self.tab_size = tab_size
        self.use_spaces = use_spaces
        self.auto_indent = auto_indent
        self._update_tab_stop_distance()
    
    def keyPressEvent(self, event):
        """Handle key press events for proper indentation."""
        # Handle Tab key
        if event.key() == Qt.Key.Key_Tab:
            self._handle_tab()
            return
        
        # Handle Shift+Tab (unindent)
        if event.key() == Qt.Key.Key_Backtab:
            self._handle_backtab()
            return
        
        # Handle Enter/Return for auto-indent
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.auto_indent:
                self._handle_return_with_indent()
                return
        
        # Default behavior for other keys
        super().keyPressEvent(event)
    
    def _handle_tab(self):
        """Handle Tab key press - insert spaces or tab based on settings."""
        cursor = self.textCursor()
        
        # Check if there's a selection
        if cursor.hasSelection():
            # Indent selected lines
            self._indent_selection(cursor)
        else:
            # Insert tab or spaces at cursor
            if self.use_spaces:
                # Calculate spaces needed to reach next tab stop
                column = cursor.columnNumber()
                spaces_to_insert = self.tab_size - (column % self.tab_size)
                cursor.insertText(' ' * spaces_to_insert)
            else:
                cursor.insertText('\t')
    
    def _handle_backtab(self):
        """Handle Shift+Tab - unindent."""
        cursor = self.textCursor()
        
        if cursor.hasSelection():
            # Unindent selected lines
            self._unindent_selection(cursor)
        else:
            # Remove indentation at cursor
            self._unindent_line(cursor)
    
    def _indent_selection(self, cursor):
        """Indent all lines in the selection."""
        # Get selection start and end
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # Move to start of selection
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        
        # Get the block at start and end
        start_block = cursor.block()
        cursor.setPosition(end)
        end_block = cursor.block()
        
        # Prepare indentation string
        indent_str = ' ' * self.tab_size if self.use_spaces else '\t'
        
        # Start edit block for undo/redo
        cursor.beginEditBlock()
        
        # Iterate through all blocks in selection
        cursor.setPosition(start_block.position())
        while True:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.insertText(indent_str)
            
            if cursor.block() == end_block:
                break
            
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        
        cursor.endEditBlock()
    
    def _unindent_selection(self, cursor):
        """Unindent all lines in the selection."""
        # Get selection start and end
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # Move to start of selection
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        
        # Get the block at start and end
        start_block = cursor.block()
        cursor.setPosition(end)
        end_block = cursor.block()
        
        # Start edit block for undo/redo
        cursor.beginEditBlock()
        
        # Iterate through all blocks in selection
        cursor.setPosition(start_block.position())
        while True:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            self._remove_indentation_from_line(cursor)
            
            if cursor.block() == end_block:
                break
            
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        
        cursor.endEditBlock()
    
    def _unindent_line(self, cursor):
        """Unindent the current line."""
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        self._remove_indentation_from_line(cursor)
        cursor.endEditBlock()
    
    def _remove_indentation_from_line(self, cursor):
        """Remove one level of indentation from the current line."""
        line_text = cursor.block().text()
        
        if not line_text:
            return
        
        # Count leading whitespace
        leading_spaces = len(line_text) - len(line_text.lstrip(' \t'))
        
        if leading_spaces == 0:
            return
        
        # Determine how much to remove
        if self.use_spaces:
            # Remove up to tab_size spaces
            to_remove = min(self.tab_size, leading_spaces)
            
            # Count actual spaces (not tabs)
            space_count = 0
            for char in line_text[:leading_spaces]:
                if char == ' ':
                    space_count += 1
                    if space_count >= to_remove:
                        break
                elif char == '\t':
                    # Treat tab as one indentation level
                    to_remove = 1
                    break
            
            to_remove = min(to_remove, space_count) if space_count > 0 else (1 if '\t' in line_text[:leading_spaces] else 0)
        else:
            # Remove one tab or up to tab_size spaces
            if line_text[0] == '\t':
                to_remove = 1
            else:
                to_remove = min(self.tab_size, leading_spaces)
        
        # Remove the indentation
        if to_remove > 0:
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, to_remove)
            cursor.removeSelectedText()
    
    def _handle_return_with_indent(self):
        """Handle Return key with auto-indentation."""
        cursor = self.textCursor()
        
        # Get current line
        current_line = cursor.block().text()
        
        # Calculate indentation of current line
        indent = self._get_line_indentation(current_line)
        
        # Check if line ends with opening brace - add extra indent
        stripped = current_line.rstrip()
        extra_indent = ''
        if stripped.endswith('{') or stripped.endswith(':'):
            extra_indent = ' ' * self.tab_size if self.use_spaces else '\t'
        
        # Insert newline and indentation
        cursor.insertText('\n' + indent + extra_indent)
    
    def _get_line_indentation(self, line: str) -> str:
        """Get the indentation string from a line."""
        indent = ''
        for char in line:
            if char in ' \t':
                indent += char
            else:
                break
        
        # Convert tabs to spaces if using spaces
        if self.use_spaces and '\t' in indent:
            indent = indent.replace('\t', ' ' * self.tab_size)
        
        return indent
    
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
