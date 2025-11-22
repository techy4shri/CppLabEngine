# Build system for compiling and running projects.

import subprocess
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from .project_config import ProjectConfig
from .toolchains import select_toolchain, ToolchainConfig


@dataclass
class BuildResult:
    success: bool
    stdout: str
    stderr: str
    command: str


def build_project(project_config: ProjectConfig) -> BuildResult:
    toolchain = select_toolchain(project_config)
    
    compiler_cmd = _build_compiler_command(project_config, toolchain)
    command_str = " ".join(compiler_cmd)
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    try:
        result = subprocess.run(
            compiler_cmd,
            cwd=project_config.path,
            capture_output=True,
            text=True,
            env=env
        )
        
        return BuildResult(
            success=(result.returncode == 0),
            stdout=result.stdout,
            stderr=result.stderr,
            command=command_str
        )
    except Exception as e:
        return BuildResult(
            success=False,
            stdout="",
            stderr=f"Build failed: {str(e)}",
            command=command_str
        )


def run_project(project_config: ProjectConfig) -> subprocess.Popen:
    toolchain = select_toolchain(project_config)
    exe_path = project_config.get_output_executable()
    
    if not Path(exe_path).exists():
        raise FileNotFoundError(f"Executable not found: {exe_path}")
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    process = subprocess.Popen(
        [exe_path],
        cwd=project_config.path,
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    return process


def _build_compiler_command(project_config: ProjectConfig, toolchain: ToolchainConfig) -> List[str]:
    compiler = "gcc" if project_config.language == "c" else "g++"
    compiler_path = str(toolchain.bin_dir / f"{compiler}.exe")
    
    cmd = [compiler_path]
    
    cmd.append(f"-std={project_config.standard}")
    
    project_path = Path(project_config.path)
    source_files = [str(project_path / f) for f in project_config.files]
    cmd.extend(source_files)
    
    output_exe = project_config.get_output_executable()
    cmd.extend(["-o", output_exe])
    
    if project_config.features.openmp and toolchain.supports_openmp:
        cmd.append("-fopenmp")
    
    if project_config.features.graphics:
        graphics_include = toolchain.include_dir
        graphics_lib = toolchain.lib_dir
        
        cmd.append(f"-I{graphics_include}")
        cmd.append(f"-L{graphics_lib}")
        cmd.extend(["-lbgi", "-lgdi32", "-lcomdlg32", "-luuid", "-loleaut32", "-lole32"])
    
    return cmd
