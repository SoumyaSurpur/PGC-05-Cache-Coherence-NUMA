#!/usr/bin/env python3
"""
================================================================================
Experiment 5: Cache Coherence and NUMA Performance Visualizer
Course: Parallel and GPU Computing (PGC)
Author: Soumya Surpur (USN: 01FE24BCI121)
Institution: KLE Technological University

Description:
  Generates publication-quality performance graphs comparing:
  1. Cache Coherence Protocol Bus Transactions & Events (MSI vs MESI vs MOESI).
  2. False Sharing Execution Time & Speedup across Thread Counts (Adjacent vs Padded).
  3. NUMA Memory Sweep Access Performance (Local vs Remote).
  4. Cache Line Stride Cliff Analysis (Empirical verification of 64-byte threshold).

Output:
  Saved high-resolution PNG charts in results/ directory.
================================================================================
"""

import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("results", exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def plot_protocols():
    protocols = ['MSI', 'MESI', 'MOESI']
    bus_tx = [4000, 3999, 3999]
    upgr = [2000, 1999, 1999]
    writebacks = [1999, 1999, 0]
    c2c = [0, 0, 1999]

    x = np.arange(len(protocols))
    width = 0.2

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    r1 = ax.bar(x - 1.5*width, bus_tx, width, label='Total Bus Tx', color='#2563EB')
    r2 = ax.bar(x - 0.5*width, upgr, width, label='Upgrades (BusUpgr)', color='#F59E0B')
    r3 = ax.bar(x + 0.5*width, writebacks, width, label='Memory Writebacks', color='#EF4444')
    r4 = ax.bar(x + 1.5*width, c2c, width, label='Cache-to-Cache (C2C)', color='#10B981')

    ax.set_ylabel('Transaction Count (1000 Iterations / 4000 Ops)', fontsize=11, fontweight='bold')
    ax.set_title('Cache Coherence Protocol Event Comparison (Adjacent Layout - False Sharing)\nMSI vs MESI vs MOESI',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(protocols, fontsize=11, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Highlight MOESI's zero writebacks
    ax.annotate('Zero Memory Writebacks!\n(C2C Transfer replaces WB)',
                xy=(2 + 0.5*width, 0), xytext=(1.5, 900),
                arrowprops=dict(facecolor='#10B981', shrink=0.08, width=1.5, headwidth=8),
                fontsize=9.5, fontweight='bold', color='#065F46',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#D1FAE5', edgecolor='#10B981'))

    plt.tight_layout()
    out_path = os.path.join("results", "protocol_bus_transactions.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved: {out_path}")

def plot_false_sharing():
    threads = [1, 2, 4]
    # Recorded data from experimental run (Screenshot 6)
    t_adjacent = [0.0224, 0.0142, 0.0085]
    t_padded = [0.0203, 0.0110, 0.0078]

    x = np.arange(len(threads))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Subplot 1: Raw Execution Time
    b1 = ax1.bar(x - width/2, t_adjacent, width, label='Adjacent (False Sharing)', color='#EF4444', alpha=0.9)
    b2 = ax1.bar(x + width/2, t_padded, width, label='Padded (64-byte Line Aligned)', color='#10B981', alpha=0.9)

    ax1.set_xlabel('Thread Count', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax1.set_title('False Sharing Impact on Execution Time\n(100 Million Counter Increments)', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{t} Thread{"s" if t>1 else ""}' for t in threads])
    ax1.legend(frameon=True)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in b1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0004, f'{yval:.4f}s', ha='center', va='bottom', fontsize=8.5)
    for bar in b2:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0004, f'{yval:.4f}s', ha='center', va='bottom', fontsize=8.5)

    # Subplot 2: Speedup of Padded over Adjacent
    speedup = [t_adj / t_pad for t_adj, t_pad in zip(t_adjacent, t_padded)]
    b3 = ax2.bar(x, speedup, width=0.45, color='#6366F1', alpha=0.9)
    ax2.axhline(1.0, color='gray', linestyle='--', linewidth=1)
    ax2.set_xlabel('Thread Count', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Speedup Factor (Adjacent / Padded)', fontsize=11, fontweight='bold')
    ax2.set_title('Padded Memory Speedup Factor\n(Overcoming False Sharing)', fontsize=11, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{t} Thread{"s" if t>1 else ""}' for t in threads])
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in b3:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f'{yval:.2f}x', ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join("results", "false_sharing_execution_time.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved: {out_path}")

def plot_numa_access():
    configs = ['Local Access\n(--membind=0)', 'Remote Access\n(--membind=1)']
    times_2t = [0.1022, 0.0961] # From Screenshot 5

    fig, ax = plt.subplots(figsize=(7, 4.8), dpi=300)
    bars = ax.bar(configs, times_2t, width=0.45, color=['#0284C7', '#D97706'], alpha=0.88)

    ax.set_ylabel('Time for 4 Passes over 512 MB (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('NUMA Memory Access Performance (2 Threads, 512 MB Sweep)\nVirtual NUMA Topology on VMware',
                 fontsize=11.5, fontweight='bold', pad=12)
    ax.set_ylim(0, 0.14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, h + 0.003, f'{h:.4f} s', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.text(0.5, 0.03, "Note: On single-socket host PC, virtual NUMA nodes share same\nphysical DDR RAM, yielding near-identical local & remote throughput.",
            ha='center', fontsize=9, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F3F4F6', edgecolor='#D1D5DB'))

    plt.tight_layout()
    out_path = os.path.join("results", "numa_access_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved: {out_path}")

def plot_stride_cliff():
    strides_bytes = [8, 16, 24, 32, 48, 56, 64, 96, 128, 256]
    times = [0.3450, 0.3250, 0.3300, 0.3220, 0.3230, 0.3400, 0.1030, 0.0270, 0.0160, 0.0170]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    ax.plot(strides_bytes, times, marker='o', linewidth=2.5, markersize=8, color='#DC2626')

    ax.axvline(64, color='#2563EB', linestyle='--', linewidth=1.8, label='64-Byte Cache Line Boundary')
    ax.axvspan(0, 64, color='#FEE2E2', alpha=0.5, label='Intra-Line False Sharing Zone (< 64B)')
    ax.axvspan(64, 260, color='#D1FAE5', alpha=0.5, label='Isolated Cache Line Zone (>= 64B)')

    ax.set_xlabel('Counter Separation Offset (Bytes)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds, lower is better)', fontsize=11, fontweight='bold')
    ax.set_title('Empirical Discovery of Cache Line Size: The 64-Byte Stride Cliff',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xlim(0, 265)
    ax.legend(frameon=True, loc='upper right', facecolor='white', framealpha=0.95)
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.annotate('The "Cliff": Latency plunges 21x\nas soon as data spans separate cache lines!',
                xy=(64, 0.1030), xytext=(90, 0.24),
                arrowprops=dict(facecolor='#2563EB', shrink=0.08, width=1.5, headwidth=8),
                fontsize=9.5, fontweight='bold', color='#1E40AF',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#DBEAFE', edgecolor='#2563EB'))

    plt.tight_layout()
    out_path = os.path.join("results", "cache_stride_cliff.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved: {out_path}")

if __name__ == '__main__':
    print("Generating comprehensive benchmark plots...")
    plot_protocols()
    plot_false_sharing()
    plot_numa_access()
    plot_stride_cliff()
    print("All plots generated successfully!")
