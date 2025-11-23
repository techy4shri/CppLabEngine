"""Improved test script with absolute paths."""

import os
import time
from pathlib import Path
from src.cpplab.core.toolchains import get_toolchains
from src.cpplab.core.project_config import ProjectConfig
from src.cpplab.core.builder import build_project, check_project

# Get available toolchains
toolchains = get_toolchains()
print(f"Available toolchains: {list(toolchains.keys())}\n")

# Create a test project config with absolute path
test_root = Path.cwd() / "test_temp"
test_project = ProjectConfig(
    name="test_perf",
    root_path=test_root.resolve(),
    language="cpp",
    standard="c++17",
    project_type="console",
    features={"graphics": False, "openmp": False},
    files=[Path("main.cpp")],
    main_file=Path("main.cpp"),
    toolchain_preference="auto"
)

# Create test directory and file
test_project.root_path.mkdir(exist_ok=True)
(test_project.root_path / "main.cpp").write_text("""#include <iostream>
int main() {
    std::cout << "Hello from performance test!" << std::endl;
    return 0;
}
""")

print("=" * 70)
print("TEST 1: First build (should compile)")
print("=" * 70)
result1 = build_project(test_project, toolchains)
print(f"Success: {result1.success}")
print(f"Elapsed: {result1.elapsed_ms:.2f}ms")
print(f"Skipped: {result1.skipped}")
print(f"Exe path: {result1.exe_path}")
if not result1.success:
    print(f"Error: {result1.stderr[:200]}")
print()

if result1.success:
    print("=" * 70)
    print("TEST 2: Second build (should skip - up to date)")
    print("=" * 70)
    time.sleep(0.1)  # Ensure time difference
    result2 = build_project(test_project, toolchains)
    print(f"Success: {result2.success}")
    print(f"Elapsed: {result2.elapsed_ms:.2f}ms")
    print(f"Skipped: {result2.skipped}")
    print(f"Message: {result2.stdout}")
    print()

    print("=" * 70)
    print("TEST 3: Modify source, rebuild should happen")
    print("=" * 70)
    time.sleep(0.1)
    (test_project.root_path / "main.cpp").write_text("""#include <iostream>
int main() {
    std::cout << "Modified version!" << std::endl;
    return 0;
}
""")
    result3 = build_project(test_project, toolchains)
    print(f"Success: {result3.success}")
    print(f"Elapsed: {result3.elapsed_ms:.2f}ms")
    print(f"Skipped: {result3.skipped}")
    print()

    print("=" * 70)
    print("TEST 4: Force rebuild")
    print("=" * 70)
    result4 = build_project(test_project, toolchains, force_rebuild=True)
    print(f"Success: {result4.success}")
    print(f"Elapsed: {result4.elapsed_ms:.2f}ms")
    print(f"Skipped: {result4.skipped}")
    print()

print("=" * 70)
print("TEST 5: Syntax check only (fast, no linking)")
print("=" * 70)
result5 = check_project(test_project, toolchains)
print(f"Success: {result5.success}")
print(f"Elapsed: {result5.elapsed_ms:.2f}ms")
print(f"Skipped: {result5.skipped}")
print(f"Exe path: {result5.exe_path} (should be None)")
if not result5.success:
    print(f"Error: {result5.stderr[:200]}")
print()

print("=" * 70)
print("TEST 6: Profiling (with CPPLAB_PROFILE_BUILDS)")
print("=" * 70)
os.environ["CPPLAB_PROFILE_BUILDS"] = "1"
result6 = build_project(test_project, toolchains, force_rebuild=True)
print(f"Build completed with profiling enabled")
print(f"Elapsed: {result6.elapsed_ms:.2f}ms")

# Check if profile file was created
profile_path = test_project.root_path / "build_profile.jsonl"
if profile_path.exists():
    print(f"\nProfile log created at: {profile_path}")
    with open(profile_path, "r") as f:
        lines = f.readlines()
        print(f"Total entries: {len(lines)}")
        if lines:
            import json
            print("\nLast entry:")
            last_entry = json.loads(lines[-1])
            print(f"  Timestamp: {last_entry['timestamp']}")
            print(f"  Project: {last_entry['project_name']}")
            print(f"  Toolchain: {last_entry['toolchain']}")
            print(f"  Success: {last_entry['success']}")
            print(f"  Skipped: {last_entry['skipped']}")
            print(f"  Elapsed: {last_entry['elapsed_ms']:.2f}ms")

# Cleanup
print("\n" + "=" * 70)
print("Cleaning up test files...")
import shutil
if test_project.root_path.exists():
    shutil.rmtree(test_project.root_path)
print("Done!")
