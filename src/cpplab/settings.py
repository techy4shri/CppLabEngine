# Application settings data model and persistence.

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AppSettings:
    """Application settings."""
    theme: str = "sky_blue"  # "classic" or "sky_blue"
    build_output_font_size: int = 11
    build_output_bold: bool = True
    incremental_builds: bool = True
    show_build_elapsed: bool = True
    # Editor settings
    tab_size: int = 4  # Number of spaces per tab
    use_spaces: bool = True  # Use spaces instead of tabs
    auto_indent: bool = True  # Automatically indent new lines


def _get_settings_path() -> Path:
    """Get settings file path."""
    config_dir = Path.home() / ".cpplab"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "settings.json"


def load_settings() -> AppSettings:
    """Load settings from disk, return defaults if missing or invalid."""
    settings_path = _get_settings_path()
    
    if not settings_path.exists():
        return AppSettings()
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate theme value
        if data.get('theme') not in ['classic', 'sky_blue']:
            data['theme'] = 'sky_blue'
        
        return AppSettings(**data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return AppSettings()


def save_settings(settings: AppSettings) -> None:
    """Save settings to disk."""
    settings_path = _get_settings_path()
    
    try:
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(settings), f, indent=2)
    except Exception:
        pass  # Silently fail if unable to save
