# Build performance benchmark harness for CppLab IDE.

import time
import csv
from pathlib import Path
from src.cpplab.core.project_config import ProjectConfig
from src.cpplab.core.builder import build_project
from src.cpplab.core.toolchains import get_toolchains


def benchmark_project(project_path: Path, toolchains: dict, num_runs: int = 5):
    """Benchmark build times for a project."""
    config = ProjectConfig.load(project_path)
    
    print(f"\nBenchmarking: {config.name}")
    print(f"  Language: {config.language}, Standard: {config.standard}")
    print(f"  Features: graphics={config.graphics}, openmp={config.openmp}")
    
    # Warm-up build
    print("  Warming up...")
    build_project(config, toolchains)
    
    # Timed runs
    times = []
    print(f"  Running {num_runs} builds...")
    
    for i in range(num_runs):
        start = time.perf_counter()
        result = build_project(config, toolchains)
        elapsed = time.perf_counter() - start
        
        if result.success:
            times.append(elapsed * 1000)  # Convert to milliseconds
        else:
            print(f"    Run {i+1}: Build failed!")
            return None
    
    return times


def main():
    """Run benchmarks for all sample projects."""
    benchmarks_root = Path(__file__).parent
    projects_dir = benchmarks_root / "projects"
    
    # Get toolchains
    toolchains = get_toolchains()
    if not toolchains:
        print("ERROR: No toolchains detected. Please install MinGW.")
        return
    
    print("=== CppLab IDE Build Performance Benchmark ===")
    print(f"Detected toolchains: {', '.join(toolchains.keys())}")
    
    # Projects to benchmark
    projects = [
        projects_dir / "hello_cpp17",
        projects_dir / "hello_openmp",
        projects_dir / "hello_graphics"
    ]
    
    results = []
    
    for project_path in projects:
        if not project_path.exists():
            print(f"\nSkipping {project_path.name}: directory not found")
            continue
        
        times = benchmark_project(project_path, toolchains)
        
        if times:
            min_time = min(times)
            max_time = max(times)
            avg_time = sum(times) / len(times)
            
            print(f"  Results:")
            print(f"    min: {min_time:.2f} ms")
            print(f"    max: {max_time:.2f} ms")
            print(f"    avg: {avg_time:.2f} ms")
            
            # Store for CSV
            for idx, elapsed in enumerate(times):
                results.append({
                    "project_name": project_path.name,
                    "run_index": idx + 1,
                    "elapsed_ms": f"{elapsed:.2f}"
                })
    
    # Write CSV results
    if results:
        csv_path = benchmarks_root / "results.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["project_name", "run_index", "elapsed_ms"])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n✓ Results saved to: {csv_path}")
    
    print("\n=== Benchmark Complete ===")


if __name__ == "__main__":
    main()
