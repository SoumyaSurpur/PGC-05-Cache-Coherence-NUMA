# ==============================================================================
# Makefile for Experiment 5: Cache Coherence (MSI, MESI, MOESI) and NUMA
# Course: Parallel and GPU Computing (PGC)
# Author: Soumya Surpur (USN: 01FE24BCI121)
# ==============================================================================

CC = gcc
CFLAGS = -O2 -Wall -fopenmp
SRC_DIR = src
BIN_DIR = bin

TARGETS = $(BIN_DIR)/coherence_sim \
          $(BIN_DIR)/false_sharing \
          $(BIN_DIR)/numa_sweep \
          $(BIN_DIR)/compare_numa \
          $(BIN_DIR)/cache_stride_cliff \
          $(BIN_DIR)/numa_cross_node_sharing

.PHONY: all clean run visualize help

all: directories $(TARGETS)

directories:
	@mkdir -p $(BIN_DIR) results outputs

$(BIN_DIR)/coherence_sim: $(SRC_DIR)/coherence_sim.c
	$(CC) -O2 -Wall $< -o $@

$(BIN_DIR)/false_sharing: $(SRC_DIR)/false_sharing.c
	$(CC) $(CFLAGS) $< -o $@

$(BIN_DIR)/numa_sweep: $(SRC_DIR)/numa_sweep.c
	$(CC) $(CFLAGS) $< -o $@

$(BIN_DIR)/compare_numa: $(SRC_DIR)/compare_numa.c
	$(CC) $(CFLAGS) $< -o $@

$(BIN_DIR)/cache_stride_cliff: $(SRC_DIR)/cache_stride_cliff.c
	$(CC) $(CFLAGS) $< -o $@

$(BIN_DIR)/numa_cross_node_sharing: $(SRC_DIR)/numa_cross_node_sharing.c
	$(CC) $(CFLAGS) $< -o $@

visualize:
	@echo "Generating performance visualization graphs..."
	python3 scripts/benchmark_visualizer.py

run: all
	@echo "=== Running Protocol Simulation ==="
	python3 $(SRC_DIR)/coherence_sim.py 1000
	@echo "\n=== Running False Sharing (2 Threads) ==="
	OMP_NUM_THREADS=2 ./$(BIN_DIR)/false_sharing adjacent
	OMP_NUM_THREADS=2 ./$(BIN_DIR)/false_sharing padded
	@echo "\n=== Running Comparison Program ==="
	./$(BIN_DIR)/compare_numa
	@echo "\n=== Running Creative Stride Cliff Benchmark ==="
	./$(BIN_DIR)/cache_stride_cliff
	@echo "\n=== Running Creative Cross-NUMA Sharing Benchmark ==="
	./$(BIN_DIR)/numa_cross_node_sharing

clean:
	rm -rf $(BIN_DIR) *.o *.exe

help:
	@echo "Experiment 5 Build Targets:"
	@echo "  make all       - Compile all C programs into bin/"
	@echo "  make run       - Execute all benchmarks"
	@echo "  make visualize - Run Python graph generation script"
	@echo "  make clean     - Remove compiled binaries and temporary files"
