# Diagnostics parser for GCC/MinGW compiler output.

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Diagnostic:
    """Represents a compiler diagnostic (error, warning, or note)."""
    file: Path
    line: int
    column: int
    message: str
    severity: str = "error"  # "error", "warning", or "note"


# Regex to match GCC/MinGW output format:
# filename:line:column: error: message
# filename:line:column: warning: message
# filename:line:column: fatal error: message
# filename:line:column: note: message
GCC_LINE_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s*(?P<kind>warning|error|fatal error|note):\s*(?P<msg>.+)$"
)


def parse_gcc_output(text: str) -> List[Diagnostic]:
    """Parse GCC/MinGW stderr into a list of diagnostics.
    
    Args:
        text: The stderr output from GCC/G++ compiler
        
    Returns:
        List of Diagnostic objects parsed from the output
    """
    diagnostics = []
    
    if not text:
        return diagnostics
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        match = GCC_LINE_RE.match(line)
        if match:
            file_path = Path(match.group('file'))
            line_num = int(match.group('line'))
            col_num = int(match.group('col'))
            kind = match.group('kind')
            msg = match.group('msg').strip()
            
            # Map kind to severity
            if kind in ('error', 'fatal error'):
                severity = 'error'
            elif kind == 'warning':
                severity = 'warning'
            elif kind == 'note':
                severity = 'note'
            else:
                severity = 'error'  # Default fallback
            
            diagnostic = Diagnostic(
                file=file_path,
                line=line_num,
                column=col_num,
                message=msg,
                severity=severity
            )
            diagnostics.append(diagnostic)
    
    return diagnostics
