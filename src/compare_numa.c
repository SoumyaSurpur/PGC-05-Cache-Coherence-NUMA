/*
 * ============================================================================
 * Experiment 5: Cache Coherence and NUMA
 * File: compare_numa.c
 * Course: Parallel and GPU Computing (PGC)
 * Author: Soumya Surpur (USN: 01FE24BCI121)
 * Institution: KLE Technological University
 *
 * Description:
 *   Comprehensive benchmark program combining:
 *     Table 1: False Sharing Benchmark (100,000,000 increments) comparing
 *              Adjacent vs Padded cache line layouts across 1, 2, and 4 threads.
 *     Table 2: NUMA Memory Sweep (512 MB buffer, 4 passes) across 1 and 2 threads.
 *
 * Compilation:
 *   gcc -O2 compare_numa.c -fopenmp -o compare_numa
 *
 * Execution:
 *   ./compare_numa
 *   Or under numactl:
 *     numactl --cpunodebind=0 --membind=0 ./compare_numa  (Local memory)
 *     numactl --cpunodebind=0 --membind=1 ./compare_numa  (Remote memory)
 *
 * Recorded Output (from lab screenshot 6):
 *   Table 1: false sharing (100000000 increments in total)
 *   Layout   | Threads | Final Count | Correctness | Time (s)
 *   ---------------------------------------------------------
 *   adjacent |       1 |   100000000 | Correct     |   0.0224
 *   padded   |       1 |   100000000 | Correct     |   0.0203
 *   ---------------------------------------------------------
 *   adjacent |       2 |   100000000 | Correct     |   0.0142
 *   padded   |       2 |   100000000 | Correct     |   0.0110
 *   ---------------------------------------------------------
 *   adjacent |       4 |   100000000 | Correct     |   0.0085
 *   padded   |       4 |   100000000 | Correct     |   0.0078
 *   ---------------------------------------------------------
 *
 *   Table 2: memory sweep of 512 MB (4 passes)
 *   Threads | Time (s)
 *   -------------------
 *         1 |   0.1129
 *         2 |   0.1049
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#if defined(_WIN32) && !defined(__linux__)
#include <malloc.h>
#define aligned_alloc(align, size) _aligned_malloc((size), (align))
#define free_aligned(ptr) _aligned_free((ptr))
#else
#define free_aligned(ptr) free((ptr))
#endif

#define N 100000000L
#define MB 512UL

double run_counters(int nt, int stride, long *total) {
    size_t bytes = ((size_t)nt * stride * sizeof(long) + 63) / 64 * 64;
    long *cnt = (long *)aligned_alloc(64, bytes);
    if (!cnt) {
        fprintf(stderr, "Memory allocation error\n");
        return -1.0;
    }
    memset(cnt, 0, bytes);

    omp_set_num_threads(nt);
    double t0 = omp_get_wtime();

    #pragma omp parallel num_threads(nt)
    {
        volatile long *p = &cnt[omp_get_thread_num() * stride];
        for (long i = 0; i < N / nt; i++) {
            (*p)++;
        }
    }

    double t = omp_get_wtime() - t0;
    *total = 0;
    for (int i = 0; i < nt; i++) {
        *total += cnt[i * stride];
    }
    free_aligned(cnt);
    return t;
}

double run_sweep(char *buf, size_t n, int nt) {
    long sum = 0;
    omp_set_num_threads(nt);
    double t0 = omp_get_wtime();

    for (int pass = 0; pass < 4; pass++) {
        #pragma omp parallel for reduction(+:sum)
        for (size_t i = 0; i < n; i += 64) {
            sum += buf[i];
        }
    }

    double t = omp_get_wtime() - t0;
    if (sum == 0) {
        printf("unexpected: sum is zero\n");
    }
    return t;
}

int main(void) {
    int tc[] = {1, 2, 4};

    printf("Table 1: false sharing (%ld increments in total)\n", N);
    printf("Layout   | Threads | Final Count | Correctness | Time (s)\n");
    printf("---------------------------------------------------------\n");

    for (int i = 0; i < 3; i++) {
        for (int s = 1; s <= 8; s *= 8) {
            long total = 0;
            double t = run_counters(tc[i], s, &total);
            printf("%-8s | %7d | %11ld | %-11s | %8.4f\n",
                   (s == 1) ? "adjacent" : "padded  ",
                   tc[i],
                   total,
                   (total == N) ? "Correct" : "INCORRECT",
                   t);
        }
        printf("---------------------------------------------------------\n");
    }

    size_t n = MB << 20;
    char *buf = (char *)malloc(n);
    if (!buf) {
        fprintf(stderr, "Failed to allocate %lu MB\n", MB);
        return 1;
    }

    /* First touch policy determines physical NUMA page placement */
    memset(buf, 1, n);

    printf("\nTable 2: memory sweep of %lu MB (4 passes)\n", MB);
    printf("Threads | Time (s)\n");
    printf("-------------------\n");

    for (int i = 0; i < 2; i++) {
        printf("%7d | %8.4f\n", tc[i], run_sweep(buf, n, tc[i]));
    }

    free(buf);
    return 0;
}
