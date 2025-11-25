# Build and run logic: compile projects and execute binaries.

import subprocess
import os
import time
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime
from .project_config import ProjectConfig
from .toolchains import ToolchainConfig, get_toolchains, select_toolchain

@dataclass
class BuildResult:
    success: bool
    command: list[str]
    stdout: str
    stderr: str
    exe_path: Optional[Path]
    elapsed_ms: float = 0.0
    skipped: bool = False


def get_executable_path(config: ProjectConfig) -> Path:
    # For standalone files (single file with just a filename, no path), 
    # put exe directly in source directory
    # For projects (multiple files or files with paths), use build subfolder
    if len(config.files) == 1 and not Path(config.files[0]).is_absolute() and "/" not in config.files[0] and "\\" not in config.files[0]:
        # Standalone file - no build folder
        return config.root_path / f"{config.name}.exe"
    else:
        # Project - use build folder
        return config.root_path / "build" / f"{config.name}.exe"


def needs_rebuild(config: ProjectConfig, exe_path: Path) -> bool:
    """Check if any source file is newer than the executable."""
    if not exe_path.exists():
        return True
    
    exe_mtime = exe_path.stat().st_mtime
    
    for source_file in config.files:
        src_path = config.root_path / source_file
        if src_path.exists() and src_path.stat().st_mtime > exe_mtime:
            return True
    
    return False


def maybe_log_profile(config: ProjectConfig, result: BuildResult, toolchain: ToolchainConfig) -> None:
    """Log build metrics to build_profile.jsonl if profiling is enabled."""
    if not os.getenv("CPPLAB_PROFILE_BUILDS"):
        return
    
    profile_data = {
        "timestamp": datetime.now().isoformat(),
        "project_name": config.name,
        "root_path": str(config.root_path),
        "language": config.language,
        "standard": config.standard,
        "project_type": config.project_type,
        "features": config.features,
        "toolchain": toolchain.name,
        "success": result.success,
        "skipped": result.skipped,
        "elapsed_ms": result.elapsed_ms
    }
    
    profile_path = config.root_path / "build_profile.jsonl"
    try:
        with open(profile_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(profile_data) + "\n")
    except Exception:
        pass  # Silently fail if logging fails


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


def check_command(config: ProjectConfig, toolchain: ToolchainConfig) -> list[str]:
    """Build compiler command for syntax-only check."""
    compiler = "gcc" if config.language == "c" else "g++"
    compiler_path = str(toolchain.bin_dir / f"{compiler}.exe")
    
    cmd = [compiler_path]
    
    source_files = [str(config.root_path / f) for f in config.files]
    cmd.extend(source_files)
    
    cmd.append(f"-std={config.standard}")
    
    if config.features.get("openmp", False) and toolchain.supports_openmp:
        cmd.append("-fopenmp")
    
    cmd.append("-fsyntax-only")
    
    return cmd


def build_project(
    config: ProjectConfig,
    toolchains: dict[str, ToolchainConfig],
    force_rebuild: bool = False
) -> BuildResult:
    toolchain = select_toolchain(config, toolchains)
    
    # Only create build directory for multi-file projects
    exe_path = get_executable_path(config)
    if "build" in str(exe_path):
        build_dir = config.root_path / "build"
        build_dir.mkdir(exist_ok=True)
    
    # Check if rebuild is needed
    if not force_rebuild and not needs_rebuild(config, exe_path):
        result = BuildResult(
            success=True,
            command=[],
            stdout="Build skipped: executable is up to date.",
            stderr="",
            exe_path=exe_path if exe_path.exists() else None,
            elapsed_ms=0.0,
            skipped=True
        )
        maybe_log_profile(config, result, toolchain)
        return result
    
    cmd = build_command(config, toolchain)
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    try:
        t0 = time.perf_counter()
        result = subprocess.run(
            cmd,
            cwd=str(config.root_path),
            capture_output=True,
            text=True,
            env=env
        )
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0
        
        exe_path = get_executable_path(config) if result.returncode == 0 else None
        
        build_result = BuildResult(
            success=(result.returncode == 0),
            command=cmd,
            stdout=result.stdout,
            stderr=result.stderr,
            exe_path=exe_path,
            elapsed_ms=elapsed_ms,
            skipped=False
        )
        maybe_log_profile(config, build_result, toolchain)
        return build_result
    except Exception as e:
        error_result = BuildResult(
            success=False,
            command=cmd,
            stdout="",
            stderr=f"Build failed: {str(e)}",
            exe_path=None,
            elapsed_ms=0.0,
            skipped=False
        )
        maybe_log_profile(config, error_result, toolchain)
        return error_result


def check_project(
    config: ProjectConfig,
    toolchains: dict[str, ToolchainConfig]
) -> BuildResult:
    """Run a syntax-only check without linking."""
    toolchain = select_toolchain(config, toolchains)
    
    cmd = check_command(config, toolchain)
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    try:
        t0 = time.perf_counter()
        result = subprocess.run(
            cmd,
            cwd=str(config.root_path),
            capture_output=True,
            text=True,
            env=env
        )
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0
        
        check_result = BuildResult(
            success=(result.returncode == 0),
            command=cmd,
            stdout=result.stdout,
            stderr=result.stderr,
            exe_path=None,
            elapsed_ms=elapsed_ms,
            skipped=False
        )
        maybe_log_profile(config, check_result, toolchain)
        return check_result
    except Exception as e:
        error_result = BuildResult(
            success=False,
            command=cmd,
            stdout="",
            stderr=f"Syntax check failed: {str(e)}",
            exe_path=None,
            elapsed_ms=0.0,
            skipped=False
        )
        maybe_log_profile(config, error_result, toolchain)
        return error_result


def run_executable(config: ProjectConfig, toolchains: dict[str, ToolchainConfig]) -> BuildResult:
    toolchain = select_toolchain(config, toolchains)
    
    exe_path = get_executable_path(config)
    
    if not exe_path.exists():
        return BuildResult(
            success=False,
            command=[str(exe_path)],
            stdout="",
            stderr="Executable not found. Please build the project first.",
            exe_path=None,
            elapsed_ms=0.0,
            skipped=False
        )
    
    env = os.environ.copy()
    env["PATH"] = str(toolchain.bin_dir) + os.pathsep + env.get("PATH", "")
    
    cmd = [str(exe_path)]
    
    try:
        # Run and capture output
        t0 = time.perf_counter()
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
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0
        
        return BuildResult(
            success=(process.returncode == 0),
            command=cmd,
            stdout=stdout,
            stderr=stderr,
            exe_path=exe_path,
            elapsed_ms=elapsed_ms,
            skipped=False
        )
    except Exception as e:
        return BuildResult(
            success=False,
            command=cmd,
            stdout="",
            stderr=f"Failed to run executable: {str(e)}",
            exe_path=exe_path,
            elapsed_ms=0.0,
            skipped=False
        )


def detect_features_from_source(source_path: Path) -> dict[str, bool]:
    """Detect graphics.h and OpenMP usage by scanning source file."""
    features = {"graphics": False, "openmp": False}
    
    try:
        with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Check for graphics.h include
        if "#include <graphics.h>" in content or '#include "graphics.h"' in content:
            features["graphics"] = True
        
        # Check for OpenMP pragmas
        if "#pragma omp" in content:
            features["openmp"] = True
            
    except Exception:
        pass  # If file can't be read, assume no special features
    
    return features


def project_config_for_single_file(
    source_path: Path,
    standard_override: Optional[str] = None,
    toolchain_preference: str = "mingw64",  # Default to 64-bit
    project_type: str = "console"  # Allow specifying project type
) -> ProjectConfig:
    """Create a synthetic ProjectConfig for a standalone source file."""
    ext = source_path.suffix.lower()
    
    # Determine language from extension
    if ext == ".c":
        language: Literal["c", "cpp"] = "c"
        standard = standard_override or "c17"
    elif ext in [".cpp", ".cc", ".cxx"]:
        language = "cpp"
        standard = standard_override or "c++17"
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
    # Auto-detect features from source if project_type is console
    features = {}
    if project_type == "console":
        detected_features = detect_features_from_source(source_path)
        features = detected_features
    elif project_type == "graphics":
        features = {"graphics": True, "openmp": False}
        toolchain_preference = "mingw32"  # Force 32-bit for graphics
    elif project_type == "openmp":
        features = {"graphics": False, "openmp": True}
        toolchain_preference = "mingw64"  # Force 64-bit for OpenMP
    
    # Put executable in the same directory as source file
    return ProjectConfig(
        name=source_path.stem,
        root_path=source_path.parent,  # Use source file's directory
        language=language,
        standard=standard,
        project_type=project_type,
        features=features,
        files=[source_path.name],  # Just filename
        main_file=source_path.name,  # Just filename
        toolchain_preference=toolchain_preference
    )


def build_single_file(
    source_path: Path,
    toolchains: dict[str, ToolchainConfig],
    standard_override: Optional[str] = None,
    toolchain_preference: str = "mingw64",
    project_type: str = "console"
) -> BuildResult:
    """Build a standalone source file without a project."""
    config = project_config_for_single_file(source_path, standard_override, toolchain_preference, project_type)
    return build_project(config, toolchains)


def run_single_file(
    source_path: Path,
    toolchains: dict[str, ToolchainConfig],
    standard_override: Optional[str] = None,
    toolchain_preference: str = "mingw64",
    project_type: str = "console"
) -> BuildResult:
    """Run a standalone source file's executable."""
    config = project_config_for_single_file(source_path, standard_override, toolchain_preference, project_type)
    return run_executable(config, toolchains)


def check_single_file(
    source_path: Path,
    toolchains: dict[str, ToolchainConfig],
    standard_override: Optional[str] = None,
    toolchain_preference: str = "mingw64",
    project_type: str = "console"
) -> BuildResult:
    """Run syntax-only check on a standalone source file."""
    config = project_config_for_single_file(source_path, standard_override, toolchain_preference, project_type)
    return check_project(config, toolchains)
