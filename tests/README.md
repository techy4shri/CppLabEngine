# CppLab IDE - Tests and Benchmarks

## Running Tests

The test suite uses `pytest`. Install pytest if not already available:

```bash
pip install pytest
```

### Run All Tests

From the repository root:

```bash
pytest
```

### Run Specific Test Files

```bash
pytest tests/test_toolchains.py
pytest tests/test_project_config.py
pytest tests/test_builder_commands.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest --cov=src/cpplab --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

## Test Structure

- **`tests/test_toolchains.py`**: Tests for toolchain detection and selection
  - Verifies `get_toolchains()` finds mingw32 and mingw64
  - Tests `select_toolchain()` behavior for different project types
  - Validates graphics projects always use mingw32
  - Confirms toolchain preference handling

- **`tests/test_project_config.py`**: Tests for project creation and configuration
  - Validates C and C++ project creation
  - Checks graphics and OpenMP project templates
  - Tests configuration save/load round-trip
  - Verifies JSON structure correctness

- **`tests/test_builder_commands.py`**: Tests for build command generation
  - Validates compiler command structure
  - Checks correct flags for standards (c11, c++17, etc.)
  - Verifies graphics projects include BGI libraries
  - Confirms OpenMP projects include `-fopenmp`
  - Tests standalone file configuration

## Running Benchmarks

The benchmark harness measures build performance for sample projects.

### Prerequisites

Ensure MinGW toolchains are installed in the expected locations.

### Run Benchmarks

From the repository root:

```bash
python benchmarks/bench_build_times.py
```

### Sample Output

```
=== CppLab IDE Build Performance Benchmark ===
Detected toolchains: mingw32, mingw64

Benchmarking: hello_cpp17
  Language: cpp, Standard: c++17
  Features: graphics=False, openmp=False
  Warming up...
  Running 5 builds...
  Results:
    min: 245.32 ms
    max: 267.89 ms
    avg: 253.12 ms

Benchmarking: hello_openmp
  Language: cpp, Standard: c++17
  Features: graphics=False, openmp=True
  Warming up...
  Running 5 builds...
  Results:
    min: 251.45 ms
    max: 278.34 ms
    avg: 262.78 ms

Benchmarking: hello_graphics
  Language: cpp, Standard: c++17
  Features: graphics=True, openmp=False
  Warming up...
  Running 5 builds...
  Results:
    min: 289.67 ms
    max: 312.45 ms
    avg: 298.23 ms

✓ Results saved to: benchmarks/results.csv
```

### Results CSV

Benchmark results are saved to `benchmarks/results.csv`:

```csv
project_name,run_index,elapsed_ms
hello_cpp17,1,245.32
hello_cpp17,2,250.12
...
```

You can import this CSV into Excel, Python pandas, or other tools for analysis.

## Benchmark Projects

Three sample projects are included:

- **`hello_cpp17`**: Basic C++17 console app
- **`hello_openmp`**: OpenMP-enabled parallel hello world
- **`hello_graphics`**: Graphics.h project with simple drawing

Each project is minimal to isolate compiler/linker performance.
