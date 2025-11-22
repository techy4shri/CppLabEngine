# Toolchain configuration and selection logic.

import os
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


def get_toolchains_base_dir() -> Path:
    script_dir = Path(__file__).parent.parent.parent.parent
    return script_dir / "compilers"


def get_mingw64_toolchain() -> ToolchainConfig:
    base = get_toolchains_base_dir()
    return ToolchainConfig(
        name="mingw64",
        root_dir=base / "mingw64",
        is_32bit=False,
        supports_openmp=True
    )


def get_mingw32_toolchain() -> ToolchainConfig:
    base = get_toolchains_base_dir()
    return ToolchainConfig(
        name="mingw32",
        root_dir=base / "mingw32",
        is_32bit=True,
        supports_openmp=False
    )


def select_toolchain(project_config) -> ToolchainConfig:
    if project_config.features.graphics:
        return get_mingw32_toolchain()
    else:
        return get_mingw64_toolchain()
