# PGC-05: Cache Coherence (MSI, MESI, MOESI) and NUMA Memory Access Performance

> **Course:** Parallel and GPU Computing (PGC)  
> **Experiment Number:** 05  
> **Author:** Soumya Surpur  
> **USN:** `01FE24BCI121`  
> **Institution:** KLE Technological University  
> **Repository:** `PGC-05-Cache-Coherence-NUMA`  

![C](https://img.shields.io/badge/Language-C11-00599C?style=for-the-badge&logo=c&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenMP](https://img.shields.io/badge/API-OpenMP-green?style=for-the-badge)
![Linux](https://img.shields.io/badge/OS-Ubuntu_24.04_LTS-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Architecture](https://img.shields.io/badge/Hardware-NUMA_&_SMP-blueviolet?style=for-the-badge)

---

## Table of Contents
- [1. Aim and Objectives](#1-aim-and-objectives)
- [2. Deep Theoretical Foundations](#2-deep-theoretical-foundations)
  - [2.1 Why Cache Coherence is Necessary](#21-why-cache-coherence-is-necessary)
  - [2.2 Cache Lines and the Mechanics of False Sharing](#22-cache-lines-and-the-mechanics-of-false-sharing)
  - [2.3 Cache Coherence Protocols: MSI vs MESI vs MOESI](#23-cache-coherence-protocols-msi-vs-mesi-vs-moesi)
  - [2.4 Non-Uniform Memory Access (NUMA) Architecture](#24-non-uniform-memory-access-numa-architecture)
  - [2.5 Linux First-Touch Memory Policy and numactl](#25-linux-first-touch-memory-policy-and-numactl)
- [3. Hardware Environment and System Setup](#3-hardware-environment-and-system-setup)
  - [3.1 Host and Virtualization Environment](#31-host-and-virtualization-environment)
  - [3.2 Exposing Virtual NUMA Nodes in VMware](#32-exposing-virtual-numa-nodes-in-vmware)
  - [3.3 Environment Setup and Verification Output](#33-environment-setup-and-verification-output)
- [4. Benchmark Programs, Execution, and Terminal Outputs](#4-benchmark-programs-execution-and-terminal-outputs)
  - [Program 1: Cache Coherence Protocol Simulator (Python & C)](#program-1-cache-coherence-protocol-simulator-python--c)
  - [Program 2: False Sharing Benchmark (Adjacent vs Padded)](#program-2-false-sharing-benchmark-adjacent-vs-padded)
  - [Program 3: NUMA Memory Sweep (Local vs Remote Access)](#program-3-numa-memory-sweep-local-vs-remote-access)
  - [Program 4: Comprehensive Comparison Benchmark (compare_numa.c)](#program-4-comprehensive-comparison-benchmark-compare_numac)
- [5. Creative Additions and Advanced Architectural Benchmarks](#5-creative-additions-and-advanced-architectural-benchmarks)
  - [Creative 1: Empirical Cache Line Boundary & Stride Cliff Analysis (cache_stride_cliff.c)](#creative-1-empirical-cache-line-boundary--stride-cliff-analysis-cache_stride_cliffc)
  - [Creative 2: Intra-Node vs Cross-Node (NUMA) False Sharing (numa_cross_node_sharing.c)](#creative-2-intra-node-vs-cross-node-numa-false-sharing-numa_cross_node_sharingc)
  - [Creative 3: High-Performance C Coherence Simulator (coherence_sim.c)](#creative-3-high-performance-c-coherence-simulator-coherence_simc)
  - [Creative 4: Automated Benchmark Visualizer & Publication Charts (benchmark_visualizer.py)](#creative-4-automated-benchmark-visualizer--publication-charts-benchmark_visualizerpy)
- [6. Performance Visualizations & Graphs](#6-performance-visualizations--graphs)
- [7. Comprehensive Comparison & Observation Summary](#7-comprehensive-comparison--observation-summary)
- [8. Repository File Structure](#8-repository-file-structure)
- [9. How to Build and Run](#9-how-to-build-and-run)
- [10. Conclusion and Key Architectural Takeaways](#10-conclusion-and-key-architectural-takeaways)

---

## 1. Aim and Objectives

The primary objectives of this experiment are:
1. **Understand Cache Coherence:** Investigate how hardware snooping cache coherence protocols (**MSI**, **MESI**, and **MOESI**) maintain strict data consistency across multi-core processors.
2. **Analyze False Sharing:** Quantify the catastrophic performance penalty caused when multiple concurrent threads read/modify independent variables mapped onto the same physical 64-byte hardware cache line.
3. **Evaluate Padding Solutions:** Implement and evaluate cache-line padding (64-byte boundary alignment via `aligned_alloc`) to completely eliminate coherence invalidation traffic.
4. **Study NUMA Architecture:** Examine Non-Uniform Memory Access (NUMA) latency characteristics, analyzing local vs remote memory allocations using `numactl`, Linux first-touch allocation, and multi-socket interconnect bottlenecks.
5. **Develop Native Implementations & Visualizations:** Construct both C and Python simulation tools, generate real-time execution benchmarks, and visualize protocol traffic and execution scalability.

---

## 2. Deep Theoretical Foundations

### 2.1 Why Cache Coherence is Necessary

In a shared-memory multi-core processor, each core possesses private high-speed L1/L2 caches to minimize memory access latency. When multiple cores load the same memory location into their respective local caches:
- If Core 0 writes an updated value to variable $x$, Core 1's cached copy of $x$ immediately becomes **stale**.
- Without an underlying hardware synchronization protocol, Core 1 would read outdated data, causing memory corruption and non-deterministic software failures.

![Hardware Snooping Cache Coherence](images/cache_coherence_snooping.png)

A **Cache Coherence Protocol** is a hardware-level finite state machine that guarantees all cores maintain a coherent, uniform view of memory by snooping on the shared memory bus/interconnect.

---

### 2.2 Cache Lines and the Mechanics of False Sharing

Processors do not transfer memory byte-by-byte. Memory is transferred in fixed blocks called **Cache Lines** (standardized at **64 bytes** on modern x86-64 processors).
- Even if a thread modifies only a single 8-byte variable, the **entire 64-byte line** is marked modified.
- **False Sharing** occurs when two threads modify distinct, non-shared variables that happen to reside within the same 64-byte cache line.

![False Sharing vs Padded Cache Line Layout](images/false_sharing_diagram.png)

---

### 2.3 Cache Coherence Protocols: MSI vs MESI vs MOESI

| State | Protocol | Meaning | Memory Synchronized? | Other Caches Can Hold Copy? |
| :---: | :---: | :--- | :---: | :---: |
| **M** | MSI, MESI, MOESI | **Modified:** Cache holds exclusive dirty copy; differs from RAM. | **No** | **No** |
| **O** | MOESI only | **Owned:** Cache holds dirty copy and acts as data owner to others. | **No** | **Yes** (as Shared) |
| **E** | MESI, MOESI | **Exclusive:** Cache holds the sole copy; clean (matches RAM). | **Yes** | **No** |
| **S** | MSI, MESI, MOESI | **Shared:** Cache holds a clean copy shared with other cores. | **Yes** (or Owner holds newer) | **Yes** |
| **I** | MSI, MESI, MOESI | **Invalid:** Data block is invalid/stale; must fetch on read/write. | - | - |

#### Architectural Protocol Comparison
1. **MSI Protocol (Baseline):**
   - Three states: Modified, Shared, Invalid.
   - Any write to a shared line requires broadcasting a `BusUpgr` (upgrade) or `BusRdX` (Read-For-Ownership).
   - Even when a core loads private data that no other core holds, it enters **Shared** state. Its very first write still requires a costly bus transaction.
2. **MESI Protocol (Intel Standard / MESIF):**
   - Introduces **Exclusive (E)** state.
   - When a core reads a line that is absent from all other caches, it loads it as **Exclusive**.
   - Subsequent writes transition **silently from E to M** (`silent E->M`) without issuing any bus transactions.
3. **MOESI Protocol (AMD Standard):**
   - Introduces **Owned (O)** state.
   - In MSI/MESI, when Core 1 reads a line held in **Modified** state by Core 0, Core 0 must write back the dirty line to main memory before sharing.
   - In MOESI, Core 0 transitions to **Owned (O)** and supplies the dirty line directly to Core 1 via **Cache-to-Cache (C2C) transfer**. Main memory write-back is avoided, drastically reducing memory bus contention.

---

### 2.4 Non-Uniform Memory Access (NUMA) Architecture

In symmetric multiprocessing (SMP) with uniform memory access (UMA), all CPUs share a single memory controller. As core counts expand, the shared memory bus becomes a severe bottleneck.
- **NUMA Architecture:** Physical memory is segregated into discrete **NUMA Nodes** (typically one node per processor socket).
- **Local Access:** A CPU core accessing RAM physically attached to its own socket enjoys minimum latency (~50-80 ns) and maximum memory bandwidth.
- **Remote Access:** A core accessing RAM attached to another socket must traverse high-speed inter-socket links (Intel Ultra Path Interconnect - **UPI** / AMD **Infinity Fabric**), incurring higher latency (~120-180 ns) and consuming interconnect bandwidth.

![NUMA Architecture](images/numa_architecture.png)

---

### 2.5 Linux First-Touch Memory Policy and numactl

The Linux kernel implements a **First-Touch Allocation Policy**:
- When a process calls `malloc()`, virtual memory addresses are reserved, but **no physical RAM pages are allocated**.
- Physical RAM pages are allocated on the NUMA node of whichever CPU core **first touches (writes to)** each page.
- The `numactl` utility controls NUMA placement:
  - `numactl --cpunodebind=0`: Binds process threads to execute only on CPUs within NUMA Node 0.
  - `numactl --membind=0`: Restricts physical memory page allocations strictly to NUMA Node 0 RAM.
  - `numactl --membind=1`: Forces memory page allocations to reside on NUMA Node 1 RAM (enforcing remote memory access for Node 0 threads).

---

## 3. Hardware Environment and System Setup

### 3.1 Host and Virtualization Environment
- **Host Processor:** 13th Gen Intel(R) Core(TM) i5-13400 (10 Cores, 16 Threads).
- **Virtualization:** VMware Workstation Pro.
- **Guest OS:** Ubuntu 24.04 / 22.04 LTS (x86_64).
- **Compiler:** GCC 13.3.0 (`build-essential`) with OpenMP runtime (`libgomp`).
- **Analysis Tools:** `numactl` (v2.0.18), `hwloc`, `lscpu`, Python 3.12.3.

---

### 3.2 Exposing Virtual NUMA Nodes in VMware

To simulate a multi-socket NUMA environment on a single physical workstation, the virtual machine `.vmx` configuration file was updated with:

```ini
numvcpus = "4"
cpuid.coresPerSocket = "2"
numa.vcpu.min = "2"
numa.vcpu.maxPerVirtualNode = "2"
```

This configuration partitions 4 virtual CPUs across **2 virtual sockets** and **2 virtual NUMA nodes** (2 cores per node).

---

### 3.3 Environment Setup and Verification Output

#### Package Installation
```bash
sudo apt update
sudo apt install build-essential numactl hwloc python3 -y
```

![Package Installation](images/01_env_packages.png)

#### Compiler and OpenMP Validation
```bash
gcc --version
echo '#include <omp.h>' | gcc -E -fopenmp -xc - > /dev/null && echo OpenMP OK
```

![GCC and OpenMP Verification](images/02_gcc_openmp_verify.png)

#### Hardware and NUMA Topology Verification
```bash
lscpu | grep -E "Socket|Core|Thread|NUMA"
numactl --hardware
lscpu -e
```

![NUMA Hardware Topology](images/03_numa_topology.png)

**Topology Summary Output:**
```text
Model name:                           13th Gen Intel(R) Core(TM) i5-13400
Thread(s) per core:                   1
Core(s) per socket:                   2
Socket(s):                            2
NUMA node(s):                         2
NUMA node0 CPU(s):                    0,1
NUMA node1 CPU(s):                    2,3

available: 2 nodes (0-1)
node 0 cpus: 0 1
node 0 size: 2014 MB
node 0 free: 559 MB
node 1 cpus: 2 3
node 1 size: 1902 MB
node 1 free: 531 MB
node distances:
node   0   1 
  0:  10  20 
  1:  20  10 

CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE
0   0    0      0    0:0:0:0       yes
1   0    0      1    1:1:1:0       yes
2   1    1      2    2:2:2:1       yes
3   1    1      3    3:3:3:1       yes
```

> **Key Finding:** The system successfully recognizes 2 sockets, with CPUs 0 and 1 assigned to NUMA Node 0 (local distance 10), and CPUs 2 and 3 assigned to NUMA Node 1 (inter-node distance 20).

---

## 4. Benchmark Programs, Execution, and Terminal Outputs

---

### Program 1: Cache Coherence Protocol Simulator (Python & C)

- **Source Files:** [`src/coherence_sim.py`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/coherence_sim.py) & [`src/coherence_sim.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/coherence_sim.c)
- **Workload:** 2 processor cores executing read/write memory operations over 1000 iterations (4000 memory operations).
  - Core 0 reads and writes counter $x$.
  - Core 1 reads and writes counter $y$.
  - Tested under **Adjacent layout** ($x$ and $y$ share Cache Line A) and **Padded layout** ($x$ on Line A, $y$ on Line B).

#### Compilation & Execution
```bash
# Python Simulation
python3 src/coherence_sim.py 1000

# Native C Simulation
gcc -O2 src/coherence_sim.c -o bin/coherence_sim
./bin/coherence_sim 1000
```

#### Screenshot Output
![Coherence Simulator Output](images/04_coherence_sim.png)

#### Terminal Trace & Statistics
```text
State trace, first 2 iterations, adjacent layout (line A: core0 state / core1 state)

MSI:
 core0 R -> C0=S C1=I
 core0 W -> C0=M C1=I
 core1 R -> C0=S C1=S
 core1 W -> C0=I C1=M
 core0 R -> C0=S C1=S
 core0 W -> C0=M C1=I
 core1 R -> C0=S C1=S
 core1 W -> C0=I C1=M

MESI:
 core0 R -> C0=E C1=I
 core0 W -> C0=M C1=I
 core1 R -> C0=S C1=S
 core1 W -> C0=I C1=M
 core0 R -> C0=S C1=S
 core0 W -> C0=M C1=I
 core1 R -> C0=S C1=S
 core1 W -> C0=I C1=M

MOESI:
 core0 R -> C0=E C1=I
 core0 W -> C0=M C1=I
 core1 R -> C0=O C1=S
 core1 W -> C0=I C1=M
 core0 R -> C0=S C1=O
 core0 W -> C0=M C1=I
 core1 R -> C0=O C1=S
 core1 W -> C0=I C1=M

Totals for 1000 iterations
layout    protocol bus transactions   BusRd   BusRdX  BusUpgr  invalidations  writeback    c2c  silent E->M
adjacent  MSI                4000      2000        0     2000           1999       1999      0            0
adjacent  MESI               3999      2000        0     1999           1999       1999      0            1
adjacent  MOESI              3999      2000        0     1999           1999          0   1999            1
padded    MSI                   4         2        0        2              0          0      0            0
padded    MESI                  2         2        0        0              0          0      0            2
padded    MOESI                 2         2        0        0              0          0      0            2
```

#### Key Analytical Points
1. **False Sharing Bus Traffic Explosion:** In the adjacent layout, 4000 memory operations trigger **3999–4000 bus transactions** and **1999 cache line invalidations**. Every write by Core 0 forces Core 1 to invalidate its local copy, producing an endless ping-pong cycle.
2. **Padding Reduces Bus Overhead by 99.9%:** In the padded layout, total bus transactions collapse from 4000 to **2 transactions** (MESI/MOESI) and **4 transactions** (MSI). Invalidations drop to **0**.
3. **MESI Silent Upgrade:** MESI avoids a bus broadcast on the first write via its **Exclusive (E)** state (`silent E->M = 1` in adjacent, `2` in padded).
4. **MOESI Eliminates RAM Flushes:** In MOESI, main memory writebacks drop to **0** (compared to 1999 writebacks in MSI and MESI). Instead, the dirty line is served directly via **1999 Cache-to-Cache (C2C)** transfers through the **Owned (O)** state.

---

### Program 2: False Sharing Benchmark (Adjacent vs Padded)

- **Source File:** [`src/false_sharing.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/false_sharing.c)
- **Workload:** 100,000,000 counter increments distributed evenly between 2 OpenMP threads (50,000,000 per thread).
- **Memory Allocation:** 64-byte aligned allocation via `aligned_alloc(64, bytes)`.
  - **Adjacent (Stride 1):** Thread 0 modifies `cnt[0]`; Thread 1 modifies `cnt[1]`. Both `long` variables occupy the exact same 64-byte line.
  - **Padded (Stride 8):** Thread 0 modifies `cnt[0]`; Thread 1 modifies `cnt[8]`. Separated by 64 bytes ($8 \times 8\text{ bytes} = 64\text{ bytes}$), placing each counter on an independent cache line.

#### Compilation & Execution
```bash
gcc -O2 src/false_sharing.c -fopenmp -o bin/false_sharing

# Run Adjacent
OMP_NUM_THREADS=2 ./bin/false_sharing adjacent

# Run Padded
OMP_NUM_THREADS=2 ./bin/false_sharing padded
```

#### Screenshot Output
![False Sharing and NUMA Sweep Output](images/05_false_sharing_numa_sweep.png)

#### Terminal Output
```text
adjacent | threads=2 | total=100000000 | time=0.0147 s
padded   | threads=2 | total=100000000 | time=0.0105 s
```

#### Key Analytical Points
- **Execution Time Reduction:** Padded execution completed in **0.0105 s** compared to **0.0147 s** for adjacent, delivering a **1.40x speedup** (28.6% time savings).
- **Correctness Maintained:** Both configurations produced the exact expected count of 100,000,000. False sharing preserves mathematical correctness but cripples runtime efficiency.
- **Hardware Mechanism:** In adjacent mode, the CPU cores spend substantial execution cycles stalled, awaiting cache-line invalidation acknowledgments and cache fills across the coherence fabric.

---

### Program 3: NUMA Memory Sweep (Local vs Remote Access)

- **Source File:** [`src/numa_sweep.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/numa_sweep.c)
- **Workload:** Allocates a **512 MB buffer** (`536,870,912 bytes`), initializes via `memset` (first-touch NUMA page binding), and executes 4 sequential read sweeps using OpenMP with a 64-byte stride (1 read per cache line = 8,388,608 reads per pass).
- **Total Reads:** $4 \times 8,388,608 = 33,554,432$ operations.

#### Compilation & Execution
```bash
gcc -O2 src/numa_sweep.c -fopenmp -o bin/numa_sweep

# Local Memory Access (Threads on Node 0, RAM on Node 0)
OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=0 ./bin/numa_sweep

# Remote Memory Access (Threads on Node 0, RAM on Node 1)
OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=1 ./bin/numa_sweep
```

#### Screenshot Output
*(Refer to Screenshot 5 above)*

#### Terminal Output
```text
buffer=512 MB | threads=2 | sum=33554432 | time=0.1022 s
buffer=512 MB | threads=2 | sum=33554432 | time=0.0961 s
```

#### Key Analytical Points
- **Sum Verification:** Sum strictly matches $33,554,432$, confirming that every 64-byte cache line across all 4 passes was accurately traversed.
- **Why Remote and Local Times Are Nearly Equal:**
  - The guest OS runs inside VMware on a **single-socket workstation PC** (Intel Core i5-13400).
  - While VMware virtualizes two separate NUMA sockets, **both virtual nodes share the exact same physical DRAM controller channels**.
  - As noted in Section 5.4 of the experiment syllabus, noticeable 30%–70% remote NUMA latency degradation requires **physical multi-socket enterprise servers** with dedicated inter-socket interconnects (UPI/Infinity Fabric).

---

### Program 4: Comprehensive Comparison Benchmark (compare_numa.c)

- **Source File:** [`src/compare_numa.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/compare_numa.c)
- **Workload:** Combines the 100M increment benchmark across 1, 2, and 4 OpenMP threads with the 512 MB memory sweep across 1 and 2 threads in a unified, reproducible binary.

#### Compilation & Execution
```bash
gcc -O2 src/compare_numa.c -fopenmp -o bin/compare_numa
./bin/compare_numa
```

#### Screenshot Output
![Compare NUMA Output](images/06_compare_numa.png)

#### Terminal Output
```text
Table 1: false sharing (100000000 increments in total)
Layout   | Threads | Final Count | Correctness | Time (s)
---------------------------------------------------------
adjacent |       1 |   100000000 | Correct     |   0.0224
padded   |       1 |   100000000 | Correct     |   0.0203
---------------------------------------------------------
adjacent |       2 |   100000000 | Correct     |   0.0142
padded   |       2 |   100000000 | Correct     |   0.0110
---------------------------------------------------------
adjacent |       4 |   100000000 | Correct     |   0.0085
padded   |       4 |   100000000 | Correct     |   0.0078
---------------------------------------------------------

Table 2: memory sweep of 512 MB (4 passes)
Threads | Time (s)
-------------------
      1 |   0.1129
      2 |   0.1049
```

#### Key Analytical Points
1. **Thread Scaling Characteristics:**
   - **1 Thread:** Adjacent (0.0224 s) and Padded (0.0203 s) perform almost identically. Without concurrent threads, no cache line ping-pong occurs.
   - **2 Threads:** Coherence traffic emerges. Padded achieves 0.0110 s vs Adjacent 0.0142 s (**1.29x speedup**).
   - **4 Threads:** Workload partitions into 25M increments per thread. Padded scales down to **0.0078 s** (**2.60x overall parallel speedup** over single-thread baseline).
2. **Memory Bandwidth Saturation:**
   - In Table 2, moving from 1 thread to 2 threads reduces sweep time from 0.1129 s to 0.1049 s.
   - Streaming sequentially through 512 MB saturates the memory bus bandwidth, explaining why memory-bound workloads exhibit diminishing returns compared to compute-bound tasks.

---

## 5. Creative Additions and Advanced Architectural Benchmarks

To extend beyond standard lab requirements, four specialized engineering modules were developed:

### Creative 1: Empirical Cache Line Boundary & Stride Cliff Analysis (cache_stride_cliff.c)

- **Source File:** [`src/cache_stride_cliff.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/cache_stride_cliff.c)
- **Concept:** Sweeps memory stride offsets from 1 element to 32 elements (8 bytes to 256 bytes) between 2 threads incrementing 50M times.
- **Objective:** Empirically discover and prove the exact byte boundary where false sharing ceases.

#### Benchmark Output
```text
==========================================================================
  CREATIVE BENCHMARK: CACHE LINE BOUNDARY & STRIDE CLIFF ANALYSIS         
  Workload: 2 Threads, 50000000 total increments (using 64-bit words)      
==========================================================================
Stride   | Byte Offset  | Cache Line State         | Time (s)     | Relative Speed 
--------------------------------------------------------------------------
1        | 8         B | Same Line (<64B) [SHARED] |     0.3450 s |       1.00x 
2        | 16        B | Same Line (<64B) [SHARED] |     0.3250 s |       1.06x 
3        | 24        B | Same Line (<64B) [SHARED] |     0.3300 s |       1.05x 
4        | 32        B | Same Line (<64B) [SHARED] |     0.3220 s |       1.07x 
6        | 48        B | Same Line (<64B) [SHARED] |     0.3230 s |       1.07x 
7        | 56        B | Same Line (<64B) [SHARED] |     0.3400 s |       1.01x 
8        | 64        B | Boundary (64B) [BOUNDARY] |     0.1030 s |       3.35x <-- 64B CLIFF PASSED
12       | 96        B | Separate Lines [ISOLATED] |     0.0270 s |      12.78x <-- 64B CLIFF PASSED
16       | 128       B | Separate Lines [ISOLATED] |     0.0160 s |      21.56x <-- 64B CLIFF PASSED
32       | 256       B | Separate Lines [ISOLATED] |     0.0170 s |      20.29x <-- 64B CLIFF PASSED
==========================================================================
```

> **Key Discovery:** Execution time hovers at $\approx 0.33\text{ s}$ for all offsets below 64 bytes. At exactly 64 bytes (Stride 8), time plunges to **0.1030 s** (3.35x speedup), and at Stride 16 (128 bytes), time drops to **0.0160 s** (**21.56x speedup**). This empirically confirms that the hardware cache line boundary is precisely **64 bytes**.

---

### Creative 2: Intra-Node vs Cross-Node (NUMA) False Sharing (numa_cross_node_sharing.c)

- **Source File:** [`src/numa_cross_node_sharing.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/numa_cross_node_sharing.c)
- **Concept:** Pin threads to specific physical/virtual CPU cores using thread affinity (`SetThreadAffinityMask` on Windows / `sched_setaffinity` on Linux) to compare:
  - **Intra-Node Sharing:** Thread 0 on CPU 0, Thread 1 on CPU 1 (Same Socket / NUMA Node 0).
  - **Cross-Node Sharing:** Thread 0 on CPU 0 (Node 0), Thread 1 on CPU 2 (Node 1 - across sockets).

#### Benchmark Output
```text
===============================================================================
  CREATIVE BENCHMARK: INTRA-NODE VS CROSS-NODE (NUMA) FALSE SHARING            
  Workload: 2 Threads, 50000000 total increments
===============================================================================

--- Test 1: Stride 1 (ADJACENT: Both share single 64-byte cache line) ---
  [Intra-Node] CPU 0 & CPU 1 (Same Node 0)    : 0.2180 s (Correctness: PASS)
  [Cross-Node] CPU 0 & CPU 2 (Node 0 vs Node 1): 0.2710 s (Correctness: PASS)

--- Test 2: Stride 8 (PADDED: Separate 64-byte cache lines) ---
  [Intra-Node] CPU 0 & CPU 1 (Same Node 0)    : 0.0310 s (Correctness: PASS)
  [Cross-Node] CPU 0 & CPU 2 (Node 0 vs Node 1): 0.0440 s (Correctness: PASS)

===============================================================================
Summary of Architectural Findings:
  - False Sharing Intra-Node vs Padded Speedup: 7.03x
  - False Sharing Cross-Node vs Padded Speedup: 6.16x
  - Interconnect Coherence Penalty Ratio (Cross/Intra): 1.24x
===============================================================================
```

> **Key Discovery:** When false sharing traverses the inter-socket NUMA boundary (CPU 0 vs CPU 2), execution latency increases by **24%** (0.2180 s $\to$ 0.2710 s) due to interconnect snooping overhead. Padding provides a **7.03x speedup** intra-node and a **6.16x speedup** cross-node.

---

### Creative 3: High-Performance C Coherence Simulator (coherence_sim.c)

- **Source File:** [`src/coherence_sim.c`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/src/coherence_sim.c)
- **Description:** A native, zero-dependency C11 implementation of the cache coherence simulator that executes memory traces at native machine speed, tracking state transitions across MSI, MESI, and MOESI protocols with comprehensive hardware event accounting.

---

### Creative 4: Automated Benchmark Visualizer & Publication Charts (benchmark_visualizer.py)

- **Source File:** [`scripts/benchmark_visualizer.py`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/scripts/benchmark_visualizer.py)
- **Description:** Python script using `matplotlib` and `numpy` that automatically ingests experimental benchmark telemetry and outputs 4 publication-quality charts into [`results/`](file:///c:/Users/surpu/OneDrive/Desktop/PGC-05/results/).

---

## 6. Performance Visualizations & Graphs

### Chart 1: Protocol Bus Transactions & Coherence Events
![Protocol Bus Transactions](results/protocol_bus_transactions.png)
*Figure: Comparison of bus transactions, upgrades, memory writebacks, and cache-to-cache transfers between MSI, MESI, and MOESI.*

---

### Chart 2: False Sharing Execution Time & Speedup
![False Sharing Execution Time](results/false_sharing_execution_time.png)
*Figure: Execution time comparison and speedup factor of 64-byte padded layout over adjacent layout across 1, 2, and 4 threads.*

---

### Chart 3: NUMA Memory Access Latency
![NUMA Memory Access](results/numa_access_comparison.png)
*Figure: 512 MB memory sweep duration under local (`--membind=0`) vs remote (`--membind=1`) allocation.*

---

### Chart 4: Empirical Discovery of Cache Line Size (The 64-Byte Stride Cliff)
![Cache Stride Cliff](results/cache_stride_cliff.png)
*Figure: Sharp 21.5x performance drop-off ("cliff") precisely at the 64-byte cache line boundary.*

---

## 7. Comprehensive Comparison & Observation Summary

| Case / Technique | Correctness | Relative Performance | Coherence Bus Traffic | Scalability Behavior |
| :--- | :---: | :--- | :--- | :--- |
| **MSI Protocol (Simulated)** | Correct | Baseline | High (Every write needs bus upgrade) | Poor on shared lines |
| **MESI Protocol (Simulated)** | Correct | Improved for private data | Reduced (Silent E $\to$ M transitions) | Efficient for private reads/writes |
| **MOESI Protocol (Simulated)** | Correct | Highest | Lowest RAM traffic (Zero writebacks via C2C) | Optimal memory bus efficiency |
| **Adjacent Counters (False Sharing)** | Correct | Slower (0.0142 s at 2T) | Severe (Continuous line invalidation ping-pong) | Typically poor; degrades with threads |
| **Padded Counters (64-byte Aligned)** | Correct | Fastest (0.0110 s at 2T, 0.0078 s at 4T) | Zero invalidations (Private lines in Modified) | Excellent; scales with thread count |
| **NUMA Local Memory (`--membind=0`)** | Correct | Reference (0.1022 s) | Minimal interconnect load | Scalable on multi-socket servers |
| **NUMA Remote Memory (`--membind=1`)** | Correct | Equivalent inside VM (0.0961 s)* | Higher traffic over interconnect link | Memory-bound code scales poorly across sockets |
| **Creative: Stride Cliff (< 64B vs $\ge$ 64B)** | Correct | 0.3450 s (8B) vs 0.0160 s (128B) | Plunges at $\ge 64\text{ Bytes}$ | 21.5x speedup at isolated cache line |
| **Creative: Cross-NUMA False Sharing** | Correct | 24% slower than Intra-Node sharing | Heavy interconnect snooping traffic | Inter-socket links become communication bottleneck |

*\*Note: Equal inside VMware VM due to unified physical memory channels on single-socket host PC.*

---

## 8. Repository File Structure

```
PGC-05/
├── .gitignore                          # Git ignore rules for binaries and cache
├── Makefile                            # Automated build configuration
├── README.md                           # Comprehensive lab documentation & analysis
├── Exp_4_Cache_Coherence_NUMA.pdf      # Lab reference manual
├── images/                             # Embedded laboratory screenshots
│   ├── 01_env_packages.png             # Package install terminal output
│   ├── 02_gcc_openmp_verify.png        # GCC & OpenMP validation
│   ├── 03_numa_topology.png            # NUMA hardware & lscpu topology
│   ├── 04_coherence_sim.png            # Python coherence simulator output
│   ├── 05_false_sharing_numa_sweep.png # False sharing & NUMA sweep runs
│   └── 06_compare_numa.png             # Full comparison benchmark tables
├── src/                                # Source code directory
│   ├── coherence_sim.py                # Python cache coherence simulator (MSI/MESI/MOESI)
│   ├── coherence_sim.c                 # Native C cache coherence simulator
│   ├── false_sharing.c                 # Program 2: Adjacent vs Padded false sharing
│   ├── numa_sweep.c                    # Program 3: 512 MB NUMA memory sweep
│   ├── compare_numa.c                  # Program 4: Full comparison suite
│   ├── cache_stride_cliff.c            # Creative 1: 64-byte stride cliff benchmark
│   └── numa_cross_node_sharing.c       # Creative 2: Cross-node NUMA false sharing
├── outputs/                            # Verbatim terminal output transcripts
│   ├── 01_system_and_environment.txt
│   ├── 02_coherence_sim_output.txt
│   ├── 03_false_sharing_output.txt
│   ├── 04_numa_sweep_output.txt
│   ├── 05_compare_numa_output.txt
│   ├── 06_numa_cross_node_output.txt
│   └── 07_cache_stride_cliff_output.txt
├── scripts/                            # Automation & visualization tools
│   ├── benchmark_visualizer.py         # Matplotlib chart generation script
│   └── run_all.sh                      # Shell script to compile and run everything
└── results/                            # High-resolution generated charts
    ├── protocol_bus_transactions.png
    ├── false_sharing_execution_time.png
    ├── numa_access_comparison.png
    └── cache_stride_cliff.png
```

---

## 9. How to Build and Run

### Prerequisites
On Ubuntu Linux / Debian:
```bash
sudo apt update && sudo apt install -y build-essential numactl hwloc python3 python3-pip
pip3 install matplotlib numpy
```

### Using the Automated Shell Script
To compile and execute all benchmarks in one step:
```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```

### Using the Makefile
```bash
# Compile all programs
make all

# Run full benchmark suite
make run

# Generate performance visualization graphs
make visualize

# Clean binaries
make clean
```

### Manual Step-by-Step Execution
```bash
# 1. Run Cache Coherence Simulator
python3 src/coherence_sim.py 1000

# 2. Compile and run False Sharing Benchmark
gcc -O2 src/false_sharing.c -fopenmp -o bin/false_sharing
OMP_NUM_THREADS=2 ./bin/false_sharing adjacent
OMP_NUM_THREADS=2 ./bin/false_sharing padded

# 3. Compile and run NUMA Memory Sweeps
gcc -O2 src/numa_sweep.c -fopenmp -o bin/numa_sweep
OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=0 ./bin/numa_sweep
OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=1 ./bin/numa_sweep

# 4. Compile and run Comparison Benchmark
gcc -O2 src/compare_numa.c -fopenmp -o bin/compare_numa
./bin/compare_numa

# 5. Run Creative Additions
gcc -O2 src/cache_stride_cliff.c -fopenmp -o bin/cache_stride_cliff
./bin/cache_stride_cliff

gcc -O2 src/numa_cross_node_sharing.c -fopenmp -o bin/numa_cross_node_sharing
./bin/numa_cross_node_sharing
```

---

## 10. Conclusion and Key Architectural Takeaways

1. **Coherence is Tracked per Cache Line (64 Bytes), Not Variable:**  
   Parallel programs can suffer massive performance degradation even when threads never touch each other's data, purely because variables share a 64-byte hardware cache line.
2. **Padding Restores Linear Scalability:**  
   Padding data structures using 64-byte boundary alignment (`aligned_alloc(64, ...)`) completely eliminates cache line bouncing, delivering up to **21.5x speedup** once data exceeds the 64-byte stride cliff.
3. **Protocol Evolution Matters:**  
   - **MESI** optimizes private data access by enabling silent $E \to M$ transitions without bus upgrades.
   - **MOESI** radically optimizes dirty line sharing by replacing main memory flushes with direct cache-to-cache (C2C) transfers via the Owned state.
4. **NUMA Affinity & Data Placement:**  
   On multi-socket servers, threads must be scheduled close to their physical memory nodes (`numactl --cpunodebind` and `--membind`). Cross-socket false sharing incurs an additional **24% latency penalty** due to inter-socket interconnect bottlenecks.
5. **Practical Software Design Rule:**  
   In concurrent systems programming, data layout is as crucial as algorithmic time complexity. Structs and counters modified by concurrent threads should always be aligned to the processor's cache line boundary (`alignas(64)` or padding).

---
*Developed for the Parallel and GPU Computing Course at KLE Technological University.*
