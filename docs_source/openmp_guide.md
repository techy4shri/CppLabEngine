# Using OpenMP (omp.h) in CppLab IDE

## What is OpenMP?

OpenMP (Open Multi-Processing) is a widely-supported API for shared-memory parallel programming in C, C++, and Fortran. It provides:

- Simple parallelization using compiler directives (`#pragma`)
- Automatic thread management
- Load balancing across CPU cores
- Portable code that works across platforms and compilers

OpenMP is ideal for:
- Scientific computing and simulations
- Data-parallel algorithms (processing large arrays)
- Multi-threaded performance optimization
- Learning parallel programming concepts

CppLab IDE includes OpenMP support via GCC's libgomp implementation in the mingw64 (64-bit) toolchain.

## When to Use OpenMP

**Good use cases:**
- CPU-intensive loops that can run independently
- Matrix operations and numerical computations
- Image/video processing algorithms
- Monte Carlo simulations
- Data analysis pipelines

**Not ideal for:**
- I/O-bound operations (file/network access)
- Code with many dependencies between iterations
- GPU-accelerated computing (use CUDA or OpenCL instead)
- Event-driven or asynchronous tasks (use threading libraries)

## Enabling OpenMP in a Project

### Method 1: Create OpenMP-Enabled Project

1. Click **File > New > New Project** (or press `Ctrl+N`)
2. Enter your project name
3. Select **Console App** as the project type
4. Check **"Enable OpenMP (multi-threading)"**
5. Click **Create**

The IDE will:
- Add `#include <omp.h>` to your starter code
- Enable the `-fopenmp` compiler flag
- Use the 64-bit MinGW toolchain (mingw64)
- Include example parallel code

### Method 2: Manual Configuration

For existing projects, you can enable OpenMP by editing `.cpplab.json`:

```json
{
  "features": {
    "openmp": true
  }
}
```

Then reload the project in the IDE.

## Basic Example Code

Here's a simple C++ program demonstrating OpenMP usage:

```cpp
#include <iostream>
#include <omp.h>

int main() {
    // Set number of threads (optional)
    omp_set_num_threads(4);
    
    // Parallel region - each thread executes this block
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        int nthreads = omp_get_num_threads();
        
        #pragma omp critical
        {
            std::cout << "Hello from thread " << tid 
                      << " of " << nthreads << std::endl;
        }
    }
    
    return 0;
}
```

### Code Explanation

- **`#include <omp.h>`**: Required header for OpenMP functions
- **`omp_set_num_threads(n)`**: Sets the number of threads to use
- **`#pragma omp parallel`**: Creates a team of threads that execute the following block
- **`omp_get_thread_num()`**: Returns the current thread's ID (0 to N-1)
- **`omp_get_num_threads()`**: Returns the total number of threads
- **`#pragma omp critical`**: Ensures only one thread executes this section at a time (prevents garbled output)

## Thread Count Control

### Method 1: In Code

```cpp
omp_set_num_threads(8);  // Use 8 threads
```

### Method 2: Environment Variable

Set `OMP_NUM_THREADS` before running:

```bash
set OMP_NUM_THREADS=4
./my_program.exe
```

### Default Behavior

If not specified, OpenMP uses the number of logical CPU cores available on your system.

## Common Parallel Patterns

### Parallel For Loop

Process array elements independently across threads:

```cpp
#include <iostream>
#include <omp.h>
#include <vector>

int main() {
    std::vector<int> data(1000);
    
    // Initialize array in parallel
    #pragma omp parallel for
    for (int i = 0; i < data.size(); i++) {
        data[i] = i * i;
    }
    
    std::cout << "Array initialized with " 
              << omp_get_max_threads() << " threads" << std::endl;
    
    return 0;
}
```

**Key Points:**
- Loop iterations are distributed across threads automatically
- Loop variable (`i`) is private to each thread
- No manual thread management needed

### Reduction Operations

Compute sum, product, min, or max in parallel:

```cpp
#include <iostream>
#include <omp.h>

int main() {
    const int N = 1000000;
    double sum = 0.0;
    
    // Parallel sum with reduction
    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < N; i++) {
        sum += i;
    }
    
    std::cout << "Sum: " << sum << std::endl;
    return 0;
}
```

**Reduction Operators:**
- `+`: Addition
- `*`: Multiplication
- `-`: Subtraction
- `&`: Bitwise AND
- `|`: Bitwise OR
- `^`: Bitwise XOR
- `&&`: Logical AND
- `||`: Logical OR

### Sections - Different Tasks in Parallel

Execute different code blocks simultaneously:

```cpp
#include <iostream>
#include <omp.h>

void task_A() { /* ... */ }
void task_B() { /* ... */ }
void task_C() { /* ... */ }

int main() {
    #pragma omp parallel sections
    {
        #pragma omp section
        task_A();
        
        #pragma omp section
        task_B();
        
        #pragma omp section
        task_C();
    }
    
    return 0;
}
```

### Private vs Shared Variables

```cpp
int main() {
    int shared_var = 0;
    int private_var = 0;
    
    #pragma omp parallel private(private_var) shared(shared_var)
    {
        private_var = omp_get_thread_num();  // Each thread has its own copy
        
        #pragma omp atomic
        shared_var++;  // All threads access the same variable (use atomic!)
    }
    
    return 0;
}
```

**Variable Scoping:**
- **shared**: All threads access the same variable (default for variables declared outside parallel region)
- **private**: Each thread gets its own copy (uninitialized)
- **firstprivate**: Private, but initialized with original value
- **reduction**: Special handling for accumulation operations

## Synchronization

### Critical Section

```cpp
#pragma omp critical
{
    // Only one thread executes this at a time
    std::cout << "Thread " << omp_get_thread_num() << std::endl;
}
```

### Atomic Operations

```cpp
#pragma omp atomic
counter++;  // Thread-safe increment
```

### Barriers

```cpp
#pragma omp parallel
{
    do_work_phase1();
    
    #pragma omp barrier  // Wait for all threads
    
    do_work_phase2();
}
```

## Performance Tips

1. **Minimize Critical Sections**: Use atomic operations or reductions instead
2. **Avoid False Sharing**: Don't have threads write to adjacent memory locations
3. **Balance Workload**: Use `schedule(dynamic)` for uneven iteration costs
4. **Reduce Overhead**: Parallelize outer loops, not inner ones
5. **Profile First**: Not all code benefits from parallelization

### Scheduling Strategies

```cpp
// Static: Divide iterations evenly at compile time (default)
#pragma omp parallel for schedule(static)

// Dynamic: Assign iterations at runtime (good for uneven work)
#pragma omp parallel for schedule(dynamic)

// Guided: Start with large chunks, decrease over time
#pragma omp parallel for schedule(guided)
```

## Measuring Performance

```cpp
#include <iostream>
#include <omp.h>

int main() {
    double start = omp_get_wtime();
    
    // Your parallel code here
    #pragma omp parallel for
    for (int i = 0; i < 1000000; i++) {
        // Work...
    }
    
    double end = omp_get_wtime();
    std::cout << "Time: " << (end - start) << " seconds" << std::endl;
    
    return 0;
}
```

## Troubleshooting

### Missing omp.h Header

**Symptom:** Compiler error: `fatal error: omp.h: No such file or directory`

**Solutions:**
1. Verify OpenMP is enabled in project settings (check `.cpplab.json`)
2. Ensure project type is **Console App** (not standalone file mode in v1)
3. Confirm mingw64 toolchain is being used

### Missing libgomp-1.dll

**Symptom:** Runtime error: "The code execution cannot proceed because libgomp-1.dll was not found"

**Solutions:**
1. Ensure `toolchains/mingw64/bin` is in your system PATH
2. Copy `libgomp-1.dll` from mingw64/bin to your project's bin folder
3. Run programs from within CppLab IDE (PATH is set automatically)

### No Performance Improvement

**Symptom:** Parallel code is slower than serial version.

**Common Causes:**
1. **Work too small**: Parallelization overhead exceeds benefit
2. **Excessive synchronization**: Too many critical sections or atomics
3. **Memory bandwidth**: Data transfer is the bottleneck, not computation
4. **False sharing**: Threads competing for cache lines

**Solutions:**
- Profile with different thread counts
- Increase work per iteration
- Minimize shared variable access
- Use `schedule(dynamic)` for better load balancing

### Race Conditions

**Symptom:** Inconsistent or incorrect results between runs.

**Solution:** Ensure proper synchronization:
```cpp
// Wrong:
counter++;

// Correct:
#pragma omp atomic
counter++;

// Or use reduction:
#pragma omp parallel for reduction(+:counter)
```

## OpenMP in Standalone Files (v1 Limitation)

**Note:** In CppLab IDE v1.0, OpenMP support is optimized for **project mode**. While standalone source files can technically include `<omp.h>`, the IDE does not automatically add `-fopenmp` for single files. 

**Workaround:** Create a minimal Console App project with OpenMP enabled.

**Future Enhancement:** v1.1+ may add OpenMP toggle for standalone mode.

## Advanced Features (Not Covered)

OpenMP includes many advanced features:
- Tasking (`#pragma omp task`)
- SIMD directives (`#pragma omp simd`)
- Target offloading (GPU support)
- Nested parallelism
- Custom reducers

Refer to the [OpenMP specification](https://www.openmp.org/specifications/) for complete documentation.

## Further Resources

- **Official OpenMP Website**: [openmp.org](https://www.openmp.org/)
- **Tutorial**: [OpenMP Tutorial by LLNL](https://hpc-tutorials.llnl.gov/openmp/)
- **Reference Card**: Search for "OpenMP Quick Reference Card PDF"
- **Books**:
  - "Using OpenMP" by Chapman, Jost, and van der Pas
  - "Parallel Programming in C with MPI and OpenMP" by Quinn

## Comparison with Other Threading APIs

| Feature | OpenMP | std::thread | pthreads |
|---------|--------|-------------|----------|
| Ease of use | High | Medium | Low |
| Portability | High | High | Unix-only |
| Fine control | Low | High | High |
| Loop parallelism | Built-in | Manual | Manual |
| Learning curve | Gentle | Moderate | Steep |

For most scientific computing and data-parallel tasks, OpenMP is the recommended choice.
