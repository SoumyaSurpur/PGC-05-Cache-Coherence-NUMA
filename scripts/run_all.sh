#!/usr/bin/env bash
# ==============================================================================
# Automated Benchmark Runner for Experiment 5: Cache Coherence & NUMA
# Course: Parallel and GPU Computing (PGC)
# Author: Soumya Surpur (USN: 01FE24BCI121)
# ==============================================================================

set -e

echo "======================================================================"
echo " Starting Benchmark Suite: Cache Coherence & NUMA Memory Performance  "
echo "======================================================================"

mkdir -p bin outputs results

# 1. Inspect Hardware & NUMA Topology
echo "[+] Step 1: Querying NUMA Topology and CPU Architecture..."
lscpu | grep -E "Socket|Core|Thread|NUMA" || true
numactl --hardware || true
lscpu -e || true

# 2. Compile All C Programs
echo -e "\n[+] Step 2: Compiling all C benchmark programs with GCC -O2 -fopenmp..."
gcc -O2 src/coherence_sim.c -o bin/coherence_sim
gcc -O2 -fopenmp src/false_sharing.c -o bin/false_sharing
gcc -O2 -fopenmp src/numa_sweep.c -o bin/numa_sweep
gcc -O2 -fopenmp src/compare_numa.c -o bin/compare_numa
gcc -O2 -fopenmp src/cache_stride_cliff.c -o bin/cache_stride_cliff
gcc -O2 -fopenmp src/numa_cross_node_sharing.c -o bin/numa_cross_node_sharing

# 3. Run Protocol Simulator
echo -e "\n[+] Step 3: Executing Cache Coherence Protocol Simulator (Python & C)..."
python3 src/coherence_sim.py 1000 | tee outputs/02_coherence_sim_output.txt

# 4. Run False Sharing Tests
echo -e "\n[+] Step 4: Running False Sharing (Adjacent vs Padded, 2 Threads)..."
OMP_NUM_THREADS=2 ./bin/false_sharing adjacent | tee outputs/03_false_sharing_output.txt
OMP_NUM_THREADS=2 ./bin/false_sharing padded | tee -a outputs/03_false_sharing_output.txt

# 5. Run NUMA Memory Sweeps
echo -e "\n[+] Step 5: Running NUMA Memory Sweeps (Local vs Remote)..."
if command -v numactl &> /dev/null; then
    OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=0 ./bin/numa_sweep | tee outputs/04_numa_sweep_output.txt
    OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=1 ./bin/numa_sweep | tee -a outputs/04_numa_sweep_output.txt
else
    echo "numactl not available; running default numa_sweep"
    OMP_NUM_THREADS=2 ./bin/numa_sweep | tee outputs/04_numa_sweep_output.txt
fi

# 6. Run Comprehensive Comparison Program
echo -e "\n[+] Step 6: Running Comprehensive Comparison Program (compare_numa)..."
./bin/compare_numa | tee outputs/05_compare_numa_output.txt

# 7. Run Creative Additions
echo -e "\n[+] Step 7: Running Creative Addition 1 (Stride Cliff Analysis)..."
./bin/cache_stride_cliff | tee outputs/07_cache_stride_cliff_output.txt

echo -e "\n[+] Step 8: Running Creative Addition 2 (Cross-Node NUMA False Sharing)..."
./bin/numa_cross_node_sharing | tee outputs/06_numa_cross_node_output.txt

# 8. Generate Visual Graphs
echo -e "\n[+] Step 9: Generating Performance Visualization Graphs..."
python3 scripts/benchmark_visualizer.py

echo -e "\n======================================================================"
echo " Benchmark Execution Complete! Results saved to outputs/ and results/  "
echo "======================================================================"
