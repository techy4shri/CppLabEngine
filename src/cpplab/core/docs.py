# Placeholder for offline documentation integration.

from pathlib import Path


def get_docs_base_dir() -> Path:
    script_dir = Path(__file__).parent.parent.parent.parent
    return script_dir / "docs"


def search_docs(query: str) -> list:
    return []
