#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

long long sum_of_squares_parallel(const int *array, long n)
{
    long long total = 0;
    int actual_threads = 0;
#pragma omp parallel
    {
#pragma omp single
        actual_threads = omp_get_num_threads();
    }
    printf("threads actually used = %d\n", actual_threads);

#pragma omp parallel for reduction(+ : total) schedule(static)
    for (long i = 0; i < n; i++)
    {
        long long v = array[i];
        total += v * v;
    }

    return total;
}