#include <iostream>
#include <omp.h>

int main() {
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        #pragma omp critical
        std::cout << "Hello from thread " << tid << std::endl;
    }
    return 0;
}
