# Tests for project configuration creation, loading, and saving.

import pytest
import json
from pathlib import Path
from src.cpplab.core.project_config import ProjectConfig, create_new_project


@pytest.fixture
def temp_project_root(tmp_path):
    """Temporary directory for test projects."""
    return tmp_path / "test_project"


def test_create_c_console_project(tmp_path):
    """C console project creates correct files."""
    project = create_new_project(
        name="TestC",
        parent_dir=tmp_path,
        language="c",
        standard="c11",
        project_type="console",
        enable_graphics=False,
        enable_openmp=False
    )
    
    assert project.name == "TestC"
    assert project.language == "c"
    assert project.standard == "c11"
    assert project.project_type == "console"
    assert not project.graphics
    assert not project.openmp
    
    # Check files exist
    config_file = project.root_path / ".cpplab.json"
    main_file = project.root_path / "src" / "main.c"
    
    assert config_file.exists()
    assert main_file.exists()
    
    # Check main.c has basic C structure
    content = main_file.read_text()
    assert "#include <stdio.h>" in content
    assert "int main()" in content


def test_create_cpp_console_project(tmp_path):
    """C++ console project creates correct files."""
    project = create_new_project(
        name="TestCPP",
        parent_dir=tmp_path,
        language="cpp",
        standard="c++17",
        project_type="console",
        enable_graphics=False,
        enable_openmp=False
    )
    
    assert project.language == "cpp"
    assert project.standard == "c++17"
    
    main_file = project.root_path / "src" / "main.cpp"
    assert main_file.exists()
    
    content = main_file.read_text()
    assert "#include <iostream>" in content
    assert "std::cout" in content


def test_create_graphics_project(tmp_path):
    """Graphics project includes graphics.h."""
    project = create_new_project(
        name="TestGraphics",
        parent_dir=tmp_path,
        language="cpp",
        standard="c++17",
        project_type="graphics",
        enable_graphics=True,
        enable_openmp=False
    )
    
    assert project.features["graphics"] == True
    assert project.graphics
    assert project.project_type == "graphics"
    
    main_file = project.root_path / "src" / "main.cpp"
    content = main_file.read_text()
    
    assert "#include <graphics.h>" in content
    assert "initgraph" in content
    assert "closegraph" in content


def test_create_openmp_project(tmp_path):
    """OpenMP project includes omp.h and pragma."""
    project = create_new_project(
        name="TestOMP",
        parent_dir=tmp_path,
        language="cpp",
        standard="c++17",
        project_type="console",
        enable_graphics=False,
        enable_openmp=True
    )
    
    assert project.features["openmp"] == True
    assert project.openmp
    
    main_file = project.root_path / "src" / "main.cpp"
    content = main_file.read_text()
    
    assert "#include <omp.h>" in content
    assert "#pragma omp" in content


def test_save_and_load_project_config(tmp_path):
    """Round-trip save and load preserves all fields."""
    # Create project
    original = create_new_project(
        name="RoundTrip",
        parent_dir=tmp_path,
        language="cpp",
        standard="c++17",
        project_type="console",
        enable_graphics=False,
        enable_openmp=True
    )
    
    # Modify some fields
    original.toolchain_preference = "mingw32"
    original.save()
    
    # Load it back
    loaded = ProjectConfig.load(original.root_path)
    
    # Verify all fields match
    assert loaded.name == original.name
    assert loaded.language == original.language
    assert loaded.standard == original.standard
    assert loaded.project_type == original.project_type
    assert loaded.graphics == original.graphics
    assert loaded.openmp == original.openmp
    assert loaded.toolchain_preference == original.toolchain_preference
    assert loaded.main_file == original.main_file
    assert loaded.root_path == original.root_path


def test_load_project_config_invalid_path():
    """Loading from non-existent path raises error."""
    with pytest.raises(FileNotFoundError):
        ProjectConfig.load(Path("/nonexistent/project"))


def test_project_config_json_structure(tmp_path):
    """Verify .cpplab.json has expected structure."""
    project = create_new_project(
        name="JSONTest",
        parent_dir=tmp_path,
        language="cpp",
        standard="c++17",
        project_type="console",
        enable_graphics=False,
        enable_openmp=False
    )
    
    config_file = project.root_path / ".cpplab.json"
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    # Check required fields
    assert "name" in data
    assert "language" in data
    assert "standard" in data
    assert "project_type" in data
    assert "features" in data
    assert "graphics" in data["features"]
    assert "openmp" in data["features"]
    assert "toolchain_preference" in data
