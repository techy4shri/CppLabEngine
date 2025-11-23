"""Tests for auto-detection of graphics.h and OpenMP in standalone files."""

from pathlib import Path
import tempfile
import shutil
from src.cpplab.core.builder import detect_features_from_source, project_config_for_single_file


def test_detect_graphics_from_source():
    """Test detection of graphics.h include."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        test_file.write_text("""#include <graphics.h>
int main() {
    initgraph();
    return 0;
}
""")
        features = detect_features_from_source(test_file)
        assert features["graphics"] == True
        assert features["openmp"] == False


def test_detect_openmp_from_source():
    """Test detection of OpenMP pragma."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        test_file.write_text("""#include <iostream>
#pragma omp parallel
int main() {
    return 0;
}
""")
        features = detect_features_from_source(test_file)
        assert features["graphics"] == False
        assert features["openmp"] == True


def test_detect_both_features():
    """Test detection of both graphics.h and OpenMP."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        test_file.write_text("""#include <graphics.h>
#pragma omp parallel
int main() {
    return 0;
}
""")
        features = detect_features_from_source(test_file)
        assert features["graphics"] == True
        assert features["openmp"] == True


def test_detect_no_features():
    """Test detection when no special features are used."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.cpp"
        test_file.write_text("""#include <iostream>
int main() {
    return 0;
}
""")
        features = detect_features_from_source(test_file)
        assert features["graphics"] == False
        assert features["openmp"] == False


def test_single_file_config_with_graphics():
    """Test that single file config includes detected graphics feature."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "graphics.cpp"
        test_file.write_text("""#include <graphics.h>
int main() { return 0; }
""")
        config = project_config_for_single_file(test_file)
        assert config.features["graphics"] == True
        assert config.features["openmp"] == False


def test_single_file_config_with_openmp():
    """Test that single file config includes detected OpenMP feature."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "openmp.cpp"
        test_file.write_text("""#pragma omp parallel
int main() { return 0; }
""")
        config = project_config_for_single_file(test_file)
        assert config.features["graphics"] == False
        assert config.features["openmp"] == True


def test_single_file_config_no_features():
    """Test that single file config has no features when none detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "normal.cpp"
        test_file.write_text("""#include <iostream>
int main() { return 0; }
""")
        config = project_config_for_single_file(test_file)
        assert config.features["graphics"] == False
        assert config.features["openmp"] == False
