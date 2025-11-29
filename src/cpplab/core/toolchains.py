# Toolchain abstraction: locates bundled MinGW compilers and selects the right one for a project.

import sys
from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolchainConfig:
    name: str
    root_dir: Path
    is_32bit: bool
    supports_openmp: bool
    
    @property
    def bin_dir(self) -> Path:
        return self.root_dir / "bin"
    
    @property
    def include_dir(self) -> Path:
        return self.root_dir / "include"
    
    @property
    def lib_dir(self) -> Path:
        return self.root_dir / "lib"
    
    @property
    def c_compiler(self) -> Path:
        return self.bin_dir / "gcc.exe"
    
    @property
    def cpp_compiler(self) -> Path:
        return self.bin_dir / "g++.exe"
    
    def is_available(self) -> bool:
        return self.bin_dir.exists() and self.cpp_compiler.exists()


def get_app_root() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent.parent.parent


@lru_cache(maxsize=1)
def get_toolchains() -> dict[str, ToolchainConfig]:
    """Get available toolchains. Cached for instant access after first call."""
    app_root = get_app_root()
    compilers_dir = app_root / "compilers"
    
    toolchains = {
        "mingw64": ToolchainConfig(
            name="mingw64",
            root_dir=compilers_dir / "mingw64",
            is_32bit=False,
            supports_openmp=True
        ),
        "mingw32": ToolchainConfig(
            name="mingw32",
            root_dir=compilers_dir / "mingw32",
            is_32bit=True,
            supports_openmp=False
        )
    }
    
    return toolchains

def intern_path(path: Path) -> Path:
    """Deduplicate path objects to save memory using string interning."""
    return Path(sys.intern(str(path)))

def select_toolchain(project_config, toolchains: Optional[dict[str, ToolchainConfig]] = None) -> ToolchainConfig:
    if toolchains is None:
        toolchains = get_toolchains()
    
    # Check if graphics is enabled
    uses_graphics = (
        project_config.project_type == "graphics" or 
        project_config.features.get("graphics", False)
    )
    # Graphics projects ALWAYS use mingw32 (32-bit), regardless of preference because that's not a preference, that's an atrocity but an obligation.
    if uses_graphics:
        selected = toolchains["mingw32"]
    else:
        # Check toolchain preference
        pref = getattr(project_config, "toolchain_preference", "auto")
        
        if pref == "mingw64" and "mingw64" in toolchains:
            selected = toolchains["mingw64"]
        elif pref == "mingw32" and "mingw32" in toolchains:
            selected = toolchains["mingw32"]
        else:
            # Auto fallback: console projects default to mingw64
            selected = toolchains.get("mingw64") or toolchains.get("mingw32")
    
    if not selected.is_available():
        raise FileNotFoundError(
            f"Toolchain '{selected.name}' not found at {selected.root_dir}. "
            f"Please ensure MinGW toolchains are installed in the compilers/ directory."
        )
    
    return selected
