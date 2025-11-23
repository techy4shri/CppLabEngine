# Tests for build command generation (without actual compilation).

import pytest
from pathlib import Path
from unittest.mock import patch
from src.cpplab.core.builder import build_command, project_config_for_single_file
from src.cpplab.core.project_config import ProjectConfig
from src.cpplab.core.toolchains import ToolchainConfig, select_toolchain


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
        files=[Path("src/main.cpp" if language == "cpp" else "src/main.c")],
        main_file=Path("src/main.cpp" if language == "cpp" else "src/main.c"),
        toolchain_preference=toolchain_preference
    )


@pytest.fixture
def fake_toolchain_mingw64():
    """Fake mingw64 toolchain."""
    return ToolchainConfig(
        name="mingw64",
        root_dir=Path("/fake/compilers/mingw64"),
        is_32bit=False,
        supports_openmp=True
    )


@pytest.fixture
def fake_toolchain_mingw32():
    """Fake mingw32 toolchain."""
    return ToolchainConfig(
        name="mingw32",
        root_dir=Path("/fake/compilers/mingw32"),
        is_32bit=True,
        supports_openmp=False
    )


@pytest.fixture
def fake_toolchains(fake_toolchain_mingw32, fake_toolchain_mingw64):
    """Dictionary of fake toolchains."""
    return {
        "mingw32": fake_toolchain_mingw32,
        "mingw64": fake_toolchain_mingw64
    }


def test_console_cpp17_command(fake_toolchains):
    """Console C++17 project generates correct command."""
    config = _make_config("TestConsole", standard="c++17")
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        toolchain = select_toolchain(config, fake_toolchains)
        cmd = build_command(config, toolchain)
        
        # Should use g++
        assert str(toolchain.bin_dir / "g++") in ' '.join(cmd)
        
        # Should have -std=c++17
        assert "-std=c++17" in cmd
        
        # Should NOT have OpenMP or graphics flags
        assert "-fopenmp" not in cmd
        assert "-lbgi" not in cmd


def test_console_c11_command(fake_toolchains):
    """Console C11 project generates correct command."""
    config = _make_config("TestC", language="c", standard="c11")
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        toolchain = select_toolchain(config, fake_toolchains)
        cmd = build_command(config, toolchain)
        
        # Should use gcc
        assert str(toolchain.bin_dir / "gcc") in ' '.join(cmd)
        
        # Should have -std=c11
        assert "-std=c11" in cmd


def test_graphics_project_command(fake_toolchains):
    """Graphics project includes BGI libraries."""
    config = _make_config("TestGraphics", project_type="graphics", graphics=True)
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        toolchain = select_toolchain(config, fake_toolchains)
        cmd = build_command(config, toolchain)
        
        # Should force mingw32
        assert toolchain.name == "mingw32"
        
        # Should have graphics libraries
        assert "-lbgi" in cmd
        assert "-lgdi32" in cmd
        assert "-lcomdlg32" in cmd
        assert "-luuid" in cmd
        assert "-loleaut32" in cmd
        assert "-lole32" in cmd


def test_openmp_project_command(fake_toolchains):
    """OpenMP project includes -fopenmp flag."""
    config = _make_config("TestOMP", openmp=True)
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        toolchain = select_toolchain(config, fake_toolchains)
        cmd = build_command(config, toolchain)
        
        # Should have OpenMP flag
        assert "-fopenmp" in cmd


def test_single_file_c_config():
    """Standalone .c file creates C11 config."""
    source_path = Path("/fake/test.c")
    
    config = project_config_for_single_file(source_path)
    
    assert config.language == "c"
    assert config.standard == "c11"
    assert config.name == "test"


def test_single_file_cpp_config():
    """Standalone .cpp file creates C++17 config."""
    source_path = Path("/fake/test.cpp")
    
    config = project_config_for_single_file(source_path)
    
    assert config.language == "cpp"
    assert config.standard == "c++17"
    assert config.name == "test"


def test_single_file_with_standard_override():
    """Standard override applies to single file."""
    source_path = Path("/fake/test.cpp")
    
    config = project_config_for_single_file(source_path, standard_override="c++20")
    
    assert config.standard == "c++20"


def test_single_file_with_toolchain_preference():
    """Toolchain preference applies to single file."""
    source_path = Path("/fake/test.cpp")
    
    config = project_config_for_single_file(
        source_path, 
        toolchain_preference="mingw32"
    )
    
    assert config.toolchain_preference == "mingw32"


def test_build_command_output_path(fake_toolchains):
    """Build command includes correct output path."""
    config = _make_config("TestOutput")
    
    with patch.object(ToolchainConfig, 'is_available', return_value=True):
        toolchain = select_toolchain(config, fake_toolchains)
        cmd = build_command(config, toolchain)
        
        # Should have -o flag with output path
        assert "-o" in cmd
        o_index = cmd.index("-o")
        output_path = cmd[o_index + 1]
        assert "bin" in output_path or output_path.endswith(".exe")
