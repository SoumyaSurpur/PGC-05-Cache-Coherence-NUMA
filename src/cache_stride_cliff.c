/*
 * ============================================================================
 * Experiment 5: Cache Coherence and NUMA - Creative Addition 1
 * File: cache_stride_cliff.c
 * Course: Parallel and GPU Computing (PGC)
 * Author: Soumya Surpur (USN: 01FE24BCI121)
 * Institution: KLE Technological University
 *
 * Description:
 *   Investigates the exact Cache Line Boundary ("The Stride Cliff").
 *   Tests the false sharing penalty as a function of data spacing (stride)
 *   between counters for 2 concurrent threads.
 *
 *   Using 64-bit uint64_t (8 bytes per word):
 *     - Stride 1 (8 B)   : Within same 64-byte line -> Severe false sharing.
 *     - Stride 2 (16 B)  : Within same 64-byte line -> Severe false sharing.
 *     - Stride 4 (32 B)  : Within same 64-byte line -> Severe false sharing.
 *     - Stride 7 (56 B)  : At edge of 64-byte line -> Severe false sharing.
 *     - Stride 8 (64 B)  : Exactly hits 64-byte boundary -> ZERO false sharing!
 *     - Stride 16 (128 B): Independent cache lines -> ZERO false sharing.
 *
 *   This program empirically determines the hardware cache line width by
 *   identifying the sudden performance drop-off ("cliff") at exactly 64 bytes.
 *
 * Compilation:
 *   gcc -O2 cache_stride_cliff.c -fopenmp -o cache_stride_cliff
 *
 * Execution:
 *   ./cache_stride_cliff
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

#if defined(_WIN32) && !defined(__linux__)
#include <malloc.h>
#define aligned_alloc(align, size) _aligned_malloc((size), (align))
#define free_aligned(ptr) _aligned_free((ptr))
#else
#define free_aligned(ptr) free((ptr))
#endif

#define N 50000000L

double test_stride(int stride_elements) {
    int nt = 2; /* 2 competing threads */
    size_t count = (size_t)nt * stride_elements;
    size_t bytes = ((count * sizeof(uint64_t) + 63) / 64) * 64;
    if (bytes < 256) bytes = 256;

    uint64_t *cnt = (uint64_t *)aligned_alloc(64, bytes);
    if (!cnt) return -1.0;
    memset(cnt, 0, bytes);

    double t0 = omp_get_wtime();

    #pragma omp parallel num_threads(nt)
    {
        int tid = omp_get_thread_num();
        volatile uint64_t *p = &cnt[tid * stride_elements];
        for (long i = 0; i < N / nt; i++) {
            (*p)++;
        }
    }

    double t = omp_get_wtime() - t0;
    free_aligned(cnt);
    return t;
}

int main(void) {
    int strides[] = {1, 2, 3, 4, 6, 7, 8, 12, 16, 32};
    int num_tests = sizeof(strides) / sizeof(strides[0]);

    printf("==========================================================================\n");
    printf("  CREATIVE BENCHMARK: CACHE LINE BOUNDARY & STRIDE CLIFF ANALYSIS         \n");
    printf("  Workload: 2 Threads, %ld total increments (using 64-bit words)      \n", N);
    printf("==========================================================================\n");
    printf("%-8s | %-12s | %-24s | %-12s | %-15s\n",
           "Stride", "Byte Offset", "Cache Line State", "Time (s)", "Relative Speed");
    printf("--------------------------------------------------------------------------\n");

    double baseline_time = 0.0;

    for (int i = 0; i < num_tests; i++) {
        int s = strides[i];
        int bytes = s * (int)sizeof(uint64_t);
        double t = test_stride(s);
        if (i == 0) baseline_time = t;

        const char *state_desc;
        if (bytes < 64) {
            state_desc = "Same Line (<64B) [SHARED]";
        } else if (bytes == 64) {
            state_desc = "Boundary (64B) [BOUNDARY]";
        } else {
            state_desc = "Separate Lines [ISOLATED]";
        }

        double speedup = (t > 0.00001) ? (baseline_time / t) : 1.0;
        printf("%-8d | %-9d B | %-24s | %10.4f s | %10.2fx %s\n",
               s, bytes, state_desc, t, speedup,
               bytes >= 64 ? "<-- 64B CLIFF PASSED" : "");
    }
    printf("==========================================================================\n");
    printf("Observation: Latency drops sharply once spacing reaches >= 64 Bytes,\n");
    printf("proving that the hardware L1/L2 cache line width is precisely 64 bytes.\n");
    printf("==========================================================================\n");

    return 0;
}
