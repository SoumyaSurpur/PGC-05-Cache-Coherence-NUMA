/*
 * ============================================================================
 * Experiment 5: Cache Coherence and NUMA
 * File: false_sharing.c
 * Course: Parallel and GPU Computing (PGC)
 * Author: Soumya Surpur (USN: 01FE24BCI121)
 * Institution: KLE Technological University
 *
 * Description:
 *   Demonstrates the performance impact of False Sharing in multi-threaded
 *   programs using OpenMP.
 *
 *   False Sharing occurs when multiple threads on different cores modify
 *   independent variables that reside on the SAME 64-byte hardware cache line.
 *   Even though the threads do not access each other's data, the cache coherence
 *   hardware invalidates the entire cache line across cores on every write,
 *   causing severe bus traffic and performance degradation (ping-pong effect).
 *
 *   - Stride 1 (Adjacent): Variables reside consecutively in memory.
 *     Thread 0 updates cnt[0], Thread 1 updates cnt[1]. Both share 1 cache line.
 *   - Stride 8 (Padded): Variables are spaced 8 `long` integers apart
 *     (8 * 8 bytes = 64 bytes). Each thread's counter gets its own private cache line.
 *
 * Compilation:
 *   gcc -O2 false_sharing.c -fopenmp -o false_sharing
 *
 * Execution:
 *   OMP_NUM_THREADS=2 ./false_sharing adjacent
 *   OMP_NUM_THREADS=2 ./false_sharing padded
 *
 * Recorded Output (from lab screenshot):
 *   adjacent | threads=2 | total=100000000 | time=0.0147 s
 *   padded   | threads=2 | total=100000000 | time=0.0105 s
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

int main(int argc, char **argv) {
    /* p = padded: 8 longs = 64 bytes (full cache line per thread) */
    int stride = (argc > 1 && argv[1][0] == 'p') ? 8 : 1;
    int nt = omp_get_max_threads();

    /* Ensure buffer size is a multiple of 64 bytes for cache-line alignment */
    size_t bytes = ((size_t)nt * stride * sizeof(long) + 63) / 64 * 64;
    long *cnt = (long *)aligned_alloc(64, bytes);
    if (!cnt) {
        fprintf(stderr, "Memory allocation error\n");
        return 1;
    }
    memset(cnt, 0, bytes);

    double t0 = omp_get_wtime();

    #pragma omp parallel
    {
        /* Each thread operates on its assigned counter index */
        volatile long *p = &cnt[omp_get_thread_num() * stride];
        for (long i = 0; i < N / nt; i++) {
            (*p)++; /* read-modify-write on own counter */
        }
    }

    double t = omp_get_wtime() - t0;

    /* Verify correctness: total must equal N */
    long total = 0;
    for (int i = 0; i < nt; i++) {
        total += cnt[i * stride];
    }

    printf("%s | threads=%d | total=%ld | time=%.4f s\n",
           stride == 1 ? "adjacent" : "padded  ", nt, total, t);

    free_aligned(cnt);
    return 0;
}
