/*
 * ============================================================================
 * Experiment 5: Cache Coherence and NUMA
 * File: numa_sweep.c
 * Course: Parallel and GPU Computing (PGC)
 * Author: Soumya Surpur (USN: 01FE24BCI121)
 * Institution: KLE Technological University
 *
 * Description:
 *   Evaluates Non-Uniform Memory Access (NUMA) memory sweep performance.
 *
 *   NUMA Systems divide physical RAM across multiple nodes (typically per socket).
 *   - Local Access: A processor core accesses RAM attached to its own socket
 *     (lowest latency, highest bandwidth).
 *   - Remote Access: A core accesses RAM attached to a different socket across
 *     the inter-socket interconnect (higher latency, lower bandwidth).
 *
 *   Linux Memory Placement (First-Touch Policy):
 *     Physical memory pages are not allocated when `malloc()` is called. They are
 *     allocated on the NUMA node of the core that FIRST writes to each page (`memset`).
 *     Using `numactl`, we can explicitly bind execution and memory to specific nodes:
 *       --cpunodebind=N : Binds threads to execute on Node N's cores.
 *       --membind=M     : Forces memory allocation to reside in Node M's RAM.
 *
 *   The program traverses a 512 MB buffer with a 64-byte stride (1 byte read
 *   per 64-byte cache line) across 4 passes to stress the memory bus and caches.
 *
 * Compilation:
 *   gcc -O2 numa_sweep.c -fopenmp -o numa_sweep
 *
 * Execution:
 *   Local node access:
 *     OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=0 ./numa_sweep
 *   Remote node access:
 *     OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=1 ./numa_sweep
 *
 * Recorded Output (from lab screenshot):
 *   buffer=512 MB | threads=2 | sum=33554432 | time=0.1022 s  (Local)
 *   buffer=512 MB | threads=2 | sum=33554432 | time=0.0961 s  (Remote)
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

int main(int argc, char **argv) {
    size_t mb = (argc > 1) ? atol(argv[1]) : 512;
    size_t n = mb << 20; /* Convert MB to bytes */

    char *buf = (char *)malloc(n);
    if (!buf) {
        fprintf(stderr, "Failed to allocate %zu MB\n", mb);
        return 1;
    }

    /*
     * First-touch policy: The memset initializes all pages. The kernel places
     * these pages onto the NUMA node specified by the current numactl policy.
     */
    memset(buf, 1, n);

    long sum = 0;
    double t0 = omp_get_wtime();

    /* Perform 4 sweeps over the memory buffer */
    for (int pass = 0; pass < 4; pass++) {
        #pragma omp parallel for reduction(+:sum)
        for (size_t i = 0; i < n; i += 64) {
            /* Read exactly one byte from each 64-byte cache line */
            sum += buf[i];
        }
    }

    double t = omp_get_wtime() - t0;

    printf("buffer=%zu MB | threads=%d | sum=%ld | time=%.4f s\n",
           mb, omp_get_max_threads(), sum, t);

    free(buf);
    return 0;
}
