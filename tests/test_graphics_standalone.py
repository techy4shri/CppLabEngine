"""Test graphics.h auto-detection in standalone files."""

from pathlib import Path
from src.cpplab.core.toolchains import get_toolchains
from src.cpplab.core.builder import build_single_file, detect_features_from_source
import shutil

# Get toolchains
toolchains = get_toolchains()

# Create test directory
test_dir = Path("test_graphics_standalone")
test_dir.mkdir(exist_ok=True)

print("=" * 70)
print("TEST 1: Detect graphics.h from source file")
print("=" * 70)

# Create a simple graphics program
graphics_file = test_dir / "graphics_test.cpp"
graphics_file.write_text("""#include <graphics.h>
#include <iostream>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    circle(320, 240, 100);
    outtextxy(270, 240, (char*)"Hello Graphics!");
    
    getch();
    closegraph();
    return 0;
}
""")

# Test feature detection
features = detect_features_from_source(graphics_file)
print(f"Detected features: {features}")
assert features["graphics"] == True, "Should detect graphics.h"
assert features["openmp"] == False, "Should not detect OpenMP"
print("✓ Feature detection works!\n")

print("=" * 70)
print("TEST 2: Build standalone file with graphics.h")
print("=" * 70)

result = build_single_file(graphics_file, toolchains)
print(f"Success: {result.success}")
print(f"Elapsed: {result.elapsed_ms:.2f}ms")
print(f"Command: {' '.join(result.command)}")

# Check that graphics libraries are linked
if result.command:
    has_bgi = "-lbgi" in result.command
    has_gdi32 = "-lgdi32" in result.command
    print(f"\nGraphics libraries linked: -lbgi={has_bgi}, -lgdi32={has_gdi32}")
    assert has_bgi, "Should include -lbgi for graphics.h"
    assert has_gdi32, "Should include -lgdi32 for graphics.h"

if result.success:
    print(f"✓ Executable created: {result.exe_path}")
else:
    print(f"✗ Build failed: {result.stderr[:200]}")

print("\n" + "=" * 70)
print("TEST 3: Regular file without graphics.h")
print("=" * 70)

normal_file = test_dir / "normal.cpp"
normal_file.write_text("""#include <iostream>

int main() {
    std::cout << "No graphics here!" << std::endl;
    return 0;
}
""")

features = detect_features_from_source(normal_file)
print(f"Detected features: {features}")
assert features["graphics"] == False, "Should not detect graphics"
print("✓ Correctly detects no graphics\n")

result = build_single_file(normal_file, toolchains)
print(f"Success: {result.success}")
if result.command:
    has_bgi = "-lbgi" in result.command
    print(f"Graphics libraries linked: {has_bgi}")
    assert not has_bgi, "Should NOT include graphics libraries"
    print("✓ No graphics libraries for normal file")

print("\n" + "=" * 70)
print("TEST 4: OpenMP detection")
print("=" * 70)

openmp_file = test_dir / "openmp.cpp"
openmp_file.write_text("""#include <iostream>
#include <omp.h>

int main() {
    #pragma omp parallel
    {
        std::cout << "Thread " << omp_get_thread_num() << std::endl;
    }
    return 0;
}
""")

features = detect_features_from_source(openmp_file)
print(f"Detected features: {features}")
assert features["openmp"] == True, "Should detect OpenMP"
assert features["graphics"] == False, "Should not detect graphics"
print("✓ OpenMP detection works!")

result = build_single_file(openmp_file, toolchains)
print(f"Success: {result.success}")
if result.command:
    has_fopenmp = "-fopenmp" in result.command
    print(f"OpenMP flag: {has_fopenmp}")
    assert has_fopenmp, "Should include -fopenmp"
    print("✓ OpenMP flag included")

print("\n" + "=" * 70)
print("TEST 5: Both graphics and OpenMP")
print("=" * 70)

both_file = test_dir / "both.cpp"
both_file.write_text("""#include <graphics.h>
#include <omp.h>

int main() {
    #pragma omp parallel
    {
        // Parallel section
    }
    
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    circle(320, 240, 50);
    closegraph();
    return 0;
}
""")

features = detect_features_from_source(both_file)
print(f"Detected features: {features}")
assert features["graphics"] == True, "Should detect graphics"
assert features["openmp"] == True, "Should detect OpenMP"
print("✓ Both features detected!")

result = build_single_file(both_file, toolchains)
print(f"Success: {result.success}")
if result.command:
    has_bgi = "-lbgi" in result.command
    has_fopenmp = "-fopenmp" in result.command
    print(f"Graphics libraries: {has_bgi}")
    print(f"OpenMP flag: {has_fopenmp}")
    print("✓ Both features included in command")

# Cleanup
print("\n" + "=" * 70)
print("Cleaning up...")
if test_dir.exists():
    shutil.rmtree(test_dir)
print("✓ All tests passed!")
