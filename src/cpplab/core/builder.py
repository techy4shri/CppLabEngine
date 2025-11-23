# Build and run logic: compile projects and execute binaries.

import subprocess
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Literal
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
        cmd.extend(["-lbgi", "-lgdi32", "-lcomdlg32", "-luuid", "-lole32", "-loleaut32"])
    
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


def run_executable(config: ProjectConfig, toolchains: dict[str, ToolchainConfig]) -> BuildResult:
    toolchain = select_toolchain(config, toolchains)
    
    exe_path = get_executable_path(config)
    
    if not exe_path.exists():
        return BuildResult(
            success=False,
            command=[str(exe_path)],
            stdout="",
            stderr="Executable not found. Please build the project first.",
            exe_path=None
        )
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    cmd = [str(exe_path)]
    
    try:
        # Run and capture output
        process = subprocess.Popen(
            cmd,
            cwd=str(config.root_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Wait for process to complete and capture output
        stdout, stderr = process.communicate()
        
        return BuildResult(
            success=(process.returncode == 0),
            command=cmd,
            stdout=stdout,
            stderr=stderr,
            exe_path=exe_path
        )
    except Exception as e:
        return BuildResult(
            success=False,
            command=cmd,
            stdout="",
            stderr=f"Failed to run executable: {str(e)}",
            exe_path=exe_path
        )


def project_config_for_single_file(
    source_path: Path,
    standard_override: Optional[str] = None,
    toolchain_preference: str = "auto"
) -> ProjectConfig:
    """Create a synthetic ProjectConfig for a standalone source file."""
    ext = source_path.suffix.lower()
    
    # Determine language from extension
    if ext == ".c":
        language: Literal["c", "cpp"] = "c"
        standard = standard_override or "c11"
    elif ext in [".cpp", ".cc", ".cxx"]:
        language = "cpp"
        standard = standard_override or "c++17"
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
    return ProjectConfig(
        name=source_path.stem,
        root_path=source_path.parent,
        language=language,
        standard=standard,
        project_type="console",
        features={"graphics": False, "openmp": False},
        files=[Path(source_path.name)],
        main_file=Path(source_path.name),
        toolchain_preference=toolchain_preference
    )


def build_single_file(
    source_path: Path,
    toolchains: dict[str, ToolchainConfig],
    standard_override: Optional[str] = None,
    toolchain_preference: str = "auto"
) -> BuildResult:
    """Build a standalone source file without a project."""
    config = project_config_for_single_file(source_path, standard_override, toolchain_preference)
    return build_project(config, toolchains)


def run_single_file(
    source_path: Path,
    toolchains: dict[str, ToolchainConfig],
    standard_override: Optional[str] = None,
    toolchain_preference: str = "auto"
) -> BuildResult:
    """Run a standalone source file's executable."""
    config = project_config_for_single_file(source_path, standard_override, toolchain_preference)
    return run_executable(config, toolchains)
