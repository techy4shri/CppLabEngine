# Tests for toolchain detection and selection logic.

import pytest
from pathlib import Path
from unittest.mock import patch
from src.cpplab.core.toolchains import get_toolchains, select_toolchain, ToolchainConfig
from src.cpplab.core.project_config import ProjectConfig


def _make_config(name, language="cpp", standard="c++17", project_type="console", 
                 graphics=False, openmp=False, toolchain_preference="auto"):
    """Helper to create ProjectConfig for tests."""
    return ProjectConfig(
        name=name,
        root_path=Path("/fake/project"),
        language=language,
        standard=standard,
        project_type=project_type,
        features={"graphics": graphics, "openmp": openmp},
        files=[Path("src/main.cpp")],
        main_file=Path("src/main.cpp"),
        toolchain_preference=toolchain_preference
    )


@pytest.fixture
def fake_app_root(tmp_path):
    """Create fake toolchain directories."""
    app_root = tmp_path / "CppLab"
    mingw32_bin = app_root / "compilers" / "mingw32" / "bin"
    mingw64_bin = app_root / "compilers" / "mingw64" / "bin"
    
    mingw32_bin.mkdir(parents=True)
    mingw64_bin.mkdir(parents=True)
    
    # Create fake gcc/g++ executables
    (mingw32_bin / "gcc.exe").touch()
    (mingw32_bin / "g++.exe").touch()
    (mingw64_bin / "gcc.exe").touch()
    (mingw64_bin / "g++.exe").touch()
    
    return app_root


def test_get_toolchains_detects_both(fake_app_root):
    """Verify get_toolchains finds mingw32 and mingw64."""
    with patch('src.cpplab.core.toolchains.get_app_root', return_value=fake_app_root):
        toolchains = get_toolchains()
        
        assert "mingw32" in toolchains
        assert "mingw64" in toolchains
        assert toolchains["mingw32"].name == "mingw32"
        assert toolchains["mingw64"].name == "mingw64"
        assert toolchains["mingw32"].bin_dir == fake_app_root / "compilers" / "mingw32" / "bin"
        assert toolchains["mingw64"].bin_dir == fake_app_root / "compilers" / "mingw64" / "bin"


def test_get_toolchains_missing_toolchains(tmp_path):
    """Verify get_toolchains returns toolchains even when directories don't exist."""
    empty_root = tmp_path / "Empty"
    empty_root.mkdir()
    
    with patch('src.cpplab.core.toolchains.get_app_root', return_value=empty_root):
        toolchains = get_toolchains()
        # Note: get_toolchains() always returns both toolchains
        # Actual existence is checked by is_available() method
        assert "mingw32" in toolchains
        assert "mingw64" in toolchains


def test_select_toolchain_graphics_forces_mingw32():
    """Graphics projects always use mingw32."""
    toolchains = {
        "mingw32": ToolchainConfig(
            name="mingw32", 
            root_dir=Path("/fake/compilers/mingw32"),
            is_32bit=True,
            supports_openmp=False
        ),
        "mingw64": ToolchainConfig(
            name="mingw64",
            root_dir=Path("/fake/compilers/mingw64"),
            is_32bit=False,
            supports_openmp=True
        )
    }
    
    config = _make_config(
        name="GraphicsTest",
        project_type="graphics",
        graphics=True,
        toolchain_preference="mingw64"  # User preference should be ignored
    )
    
    # Mock is_available to always return True for tests
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        selected = select_toolchain(config, toolchains)
        assert selected.name == "mingw32"


def test_select_toolchain_preference_mingw64():
    """Console project with mingw64 preference selects mingw64."""
    toolchains = {
        "mingw32": ToolchainConfig(
            name="mingw32",
            root_dir=Path("/fake/compilers/mingw32"),
            is_32bit=True,
            supports_openmp=False
        ),
        "mingw64": ToolchainConfig(
            name="mingw64",
            root_dir=Path("/fake/compilers/mingw64"),
            is_32bit=False,
            supports_openmp=True
        )
    }
    
    config = _make_config(
        name="ConsoleTest",
        toolchain_preference="mingw64"
    )
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        selected = select_toolchain(config, toolchains)
        assert selected.name == "mingw64"


def test_select_toolchain_preference_mingw32():
    """Console project with mingw32 preference selects mingw32."""
    toolchains = {
        "mingw32": ToolchainConfig(
            name="mingw32",
            root_dir=Path("/fake/compilers/mingw32"),
            is_32bit=True,
            supports_openmp=False
        ),
        "mingw64": ToolchainConfig(
            name="mingw64",
            root_dir=Path("/fake/compilers/mingw64"),
            is_32bit=False,
            supports_openmp=True
        )
    }
    
    config = _make_config(
        name="ConsoleTest",
        toolchain_preference="mingw32"
    )
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        selected = select_toolchain(config, toolchains)
        assert selected.name == "mingw32"


def test_select_toolchain_auto_defaults_mingw64():
    """Console project with auto preference defaults to mingw64."""
    toolchains = {
        "mingw32": ToolchainConfig(
            name="mingw32",
            root_dir=Path("/fake/compilers/mingw32"),
            is_32bit=True,
            supports_openmp=False
        ),
        "mingw64": ToolchainConfig(
            name="mingw64",
            root_dir=Path("/fake/compilers/mingw64"),
            is_32bit=False,
            supports_openmp=True
        )
    }
    
    config = _make_config(
        name="ConsoleTest",
        toolchain_preference="auto"
    )
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        selected = select_toolchain(config, toolchains)
        assert selected.name == "mingw64"


def test_select_toolchain_openmp_prefers_mingw64():
    """OpenMP projects prefer mingw64 when auto."""
    toolchains = {
        "mingw32": ToolchainConfig(
            name="mingw32",
            root_dir=Path("/fake/compilers/mingw32"),
            is_32bit=True,
            supports_openmp=False
        ),
        "mingw64": ToolchainConfig(
            name="mingw64",
            root_dir=Path("/fake/compilers/mingw64"),
            is_32bit=False,
            supports_openmp=True
        )
    }
    
    config = _make_config(
        name="OMPTest",
        openmp=True,
        toolchain_preference="auto"
    )
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        selected = select_toolchain(config, toolchains)
        assert selected.name == "mingw64"
