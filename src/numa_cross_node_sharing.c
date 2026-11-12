/*
 * ============================================================================
 * Experiment 5: Cache Coherence and NUMA - Creative Addition 2
 * File: numa_cross_node_sharing.c
 * Course: Parallel and GPU Computing (PGC)
 * Author: Soumya Surpur (USN: 01FE24BCI121)
 * Institution: KLE Technological University
 *
 * Description:
 *   Investigates Cross-NUMA False Sharing vs Intra-NUMA False Sharing.
 *
 *   In modern multi-socket/NUMA architectures:
 *     - Intra-Node Coherence (Cores on same NUMA socket):
 *       Cache invalidation and line transfers stay within the local socket,
 *       mediated by shared L3 cache or intra-chip ring/mesh interconnect.
 *     - Cross-Node Coherence (Cores on different NUMA sockets):
 *       Cache invalidations and dirty line snooping MUST traverse the physical
 *       inter-socket link (e.g., Intel UPI / AMD Infinity Fabric / QPI).
 *
 *   This benchmark measures:
 *     Case A: Intra-Node Adjacent (CPUs on Node 0) -> Local False Sharing
 *     Case B: Cross-Node Adjacent (CPU on Node 0 vs CPU on Node 1) -> Inter-Socket False Sharing
 *     Case C: Intra-Node Padded (Separate 64B cache lines on Node 0)
 *     Case D: Cross-Node Padded (Separate 64B cache lines across Node 0 & 1)
 *
 * Compilation:
 *   gcc -O2 numa_cross_node_sharing.c -fopenmp -o numa_cross_node_sharing
 *
 * Execution:
 *   ./numa_cross_node_sharing
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#include <malloc.h>
#define aligned_alloc(align, size) _aligned_malloc((size), (align))
#define free_aligned(ptr) _aligned_free((ptr))

void pin_thread_to_cpu(int cpu_id) {
    DWORD_PTR mask = (DWORD_PTR)1 << cpu_id;
    SetThreadAffinityMask(GetCurrentThread(), mask);
}
#else
#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#define free_aligned(ptr) free((ptr))

void pin_thread_to_cpu(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);
}
#endif

#define N 50000000L

double benchmark_pinned(int cpu0, int cpu1, int stride_elements, long *out_total) {
    size_t count = (size_t)2 * stride_elements;
    size_t bytes = ((count * sizeof(uint64_t) + 63) / 64) * 64;
    if (bytes < 256) bytes = 256;

    uint64_t *cnt = (uint64_t *)aligned_alloc(64, bytes);
    if (!cnt) return -1.0;
    memset(cnt, 0, bytes);

    double t0 = omp_get_wtime();

    #pragma omp parallel num_threads(2)
    {
        int tid = omp_get_thread_num();
        int target_cpu = (tid == 0) ? cpu0 : cpu1;
        pin_thread_to_cpu(target_cpu);

        volatile uint64_t *p = &cnt[tid * stride_elements];
        for (long i = 0; i < N / 2; i++) {
            (*p)++;
        }
    }

    double t = omp_get_wtime() - t0;
    *out_total = cnt[0] + cnt[1 * stride_elements];
    free_aligned(cnt);
    return t;
}

int main(void) {
    printf("===============================================================================\n");
    printf("  CREATIVE BENCHMARK: INTRA-NODE VS CROSS-NODE (NUMA) FALSE SHARING            \n");
    printf("  Workload: 2 Threads, %ld total increments\n", N);
    printf("===============================================================================\n");

    /*
     * Mapping for dual-node system (e.g. Node 0 = CPU 0, 1; Node 1 = CPU 2, 3)
     * If running on single-socket laptop, pins to CPU 0, 1 (same core/cluster)
     * vs CPU 0, 2 (different core/CCX).
     */
    int cpu_node0_a = 0;
    int cpu_node0_b = 1;
    int cpu_node1_a = 2;

    long total = 0;

    printf("\n--- Test 1: Stride 1 (ADJACENT: Both share single 64-byte cache line) ---\n");
    double t_intra_adj = benchmark_pinned(cpu_node0_a, cpu_node0_b, 1, &total);
    printf("  [Intra-Node] CPU %d & CPU %d (Same Node 0)    : %.4f s (Correctness: %s)\n",
           cpu_node0_a, cpu_node0_b, t_intra_adj, (total == N) ? "PASS" : "FAIL");

    double t_cross_adj = benchmark_pinned(cpu_node0_a, cpu_node1_a, 1, &total);
    printf("  [Cross-Node] CPU %d & CPU %d (Node 0 vs Node 1): %.4f s (Correctness: %s)\n",
           cpu_node0_a, cpu_node1_a, t_cross_adj, (total == N) ? "PASS" : "FAIL");

    printf("\n--- Test 2: Stride 8 (PADDED: Separate 64-byte cache lines) ---\n");
    double t_intra_pad = benchmark_pinned(cpu_node0_a, cpu_node0_b, 8, &total);
    printf("  [Intra-Node] CPU %d & CPU %d (Same Node 0)    : %.4f s (Correctness: %s)\n",
           cpu_node0_a, cpu_node0_b, t_intra_pad, (total == N) ? "PASS" : "FAIL");

    double t_cross_pad = benchmark_pinned(cpu_node0_a, cpu_node1_a, 8, &total);
    printf("  [Cross-Node] CPU %d & CPU %d (Node 0 vs Node 1): %.4f s (Correctness: %s)\n",
           cpu_node0_a, cpu_node1_a, t_cross_pad, (total == N) ? "PASS" : "FAIL");

    printf("\n===============================================================================\n");
    printf("Summary of Architectural Findings:\n");
    printf("  - False Sharing Intra-Node vs Padded Speedup: %.2fx\n",
           t_intra_adj / (t_intra_pad > 0 ? t_intra_pad : 0.001));
    printf("  - False Sharing Cross-Node vs Padded Speedup: %.2fx\n",
           t_cross_adj / (t_cross_pad > 0 ? t_cross_pad : 0.001));
    printf("  - Interconnect Coherence Penalty Ratio (Cross/Intra): %.2fx\n",
           t_cross_adj / (t_intra_adj > 0 ? t_intra_adj : 0.001));
    printf("===============================================================================\n");

    return 0;
}
