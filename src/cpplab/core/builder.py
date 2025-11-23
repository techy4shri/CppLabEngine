# Build and run logic: compile projects and execute binaries.

import subprocess
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from .project_config import ProjectConfig
from .toolchains import ToolchainConfig, get_toolchains, select_toolchain


@dataclass
class BuildResult:
    success: bool
    command: list[str]
    stdout: str
    stderr: str
    exe_path: Optional[Path]


def get_executable_path(config: ProjectConfig) -> Path:
    return config.root_path / "build" / f"{config.name}.exe"


def build_command(config: ProjectConfig, toolchain: ToolchainConfig) -> list[str]:
    compiler = "gcc" if config.language == "c" else "g++"
    compiler_path = str(toolchain.bin_dir / f"{compiler}.exe")
    
    cmd = [compiler_path]
    
    source_files = [str(config.root_path / f) for f in config.files]
    cmd.extend(source_files)
    
    cmd.append(f"-std={config.standard}")
    
    if config.features.get("openmp", False) and toolchain.supports_openmp:
        cmd.append("-fopenmp")
    
    exe_path = get_executable_path(config)
    cmd.extend(["-o", str(exe_path)])
    
    if config.features.get("graphics", False):
        cmd.extend(["-lbgi", "-lgdi32", "-lcomdlg32", "-luuid"])
    
    return cmd


def build_project(config: ProjectConfig, toolchains: dict[str, ToolchainConfig]) -> BuildResult:
    toolchain = select_toolchain(config, toolchains)
    
    build_dir = config.root_path / "build"
    build_dir.mkdir(exist_ok=True)
    
    cmd = build_command(config, toolchain)
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(config.root_path),
            capture_output=True,
            text=True,
            env=env
        )
        
        exe_path = get_executable_path(config) if result.returncode == 0 else None
        
        return BuildResult(
            success=(result.returncode == 0),
            command=cmd,
            stdout=result.stdout,
            stderr=result.stderr,
            exe_path=exe_path
        )
    except Exception as e:
        return BuildResult(
            success=False,
            command=cmd,
            stdout="",
            stderr=f"Build failed: {str(e)}",
            exe_path=None
        )


def run_executable(config: ProjectConfig, toolchains: dict[str, ToolchainConfig]) -> Optional[subprocess.Popen]:
    toolchain = select_toolchain(config, toolchains)
    
    exe_path = get_executable_path(config)
    
    if not exe_path.exists():
        return None
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    process = subprocess.Popen(
        [str(exe_path)],
        cwd=str(config.root_path),
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    return process
