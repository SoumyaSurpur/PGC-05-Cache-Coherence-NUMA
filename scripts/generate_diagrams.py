#!/usr/bin/env python3
"""
Generate high-resolution architecture diagrams to replace ASCII art:
1. images/numa_architecture.png
2. images/false_sharing_diagram.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ArrowStyle

def create_numa_diagram():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#0F172A') # Dark slate background
    ax.set_facecolor('#0F172A')

    # Title
    ax.text(6.5, 7.1, "Non-Uniform Memory Access (NUMA) Architecture",
            ha='center', va='center', color='#F8FAFC', fontsize=18, fontweight='bold', fontfamily='sans-serif')
    ax.text(6.5, 6.7, "Dual-Socket Virtual NUMA Topology (VMware Configuration: Node 0 & Node 1)",
            ha='center', va='center', color='#94A3B8', fontsize=11, fontfamily='sans-serif')

    # ================== NUMA NODE 0 (Left) ==================
    # Node 0 Box
    node0_box = FancyBboxPatch((0.6, 0.6), 4.8, 5.7, boxstyle="round,pad=0.2",
                               fc='#1E293B', ec='#38BDF8', lw=2.5)
    ax.add_patch(node0_box)
    ax.text(3.0, 6.0, "NUMA NODE 0 (Socket 0)", color='#38BDF8', fontsize=14, fontweight='bold', ha='center')

    # Core 0 Box
    c0 = FancyBboxPatch((0.9, 4.4), 1.9, 1.2, boxstyle="round,pad=0.1", fc='#0F172A', ec='#64748B', lw=1.5)
    ax.add_patch(c0)
    ax.text(1.85, 5.2, "Core 0", color='#F8FAFC', fontsize=12, fontweight='bold', ha='center')
    ax.text(1.85, 4.75, "L1 / L2 Cache\n(32KB / 1.25MB)", color='#94A3B8', fontsize=8.5, ha='center')

    # Core 1 Box
    c1 = FancyBboxPatch((3.2, 4.4), 1.9, 1.2, boxstyle="round,pad=0.1", fc='#0F172A', ec='#64748B', lw=1.5)
    ax.add_patch(c1)
    ax.text(4.15, 5.2, "Core 1", color='#F8FAFC', fontsize=12, fontweight='bold', ha='center')
    ax.text(4.15, 4.75, "L1 / L2 Cache\n(32KB / 1.25MB)", color='#94A3B8', fontsize=8.5, ha='center')

    # Arrows from cores to L3
    arr0 = FancyArrowPatch((1.85, 4.3), (2.4, 3.7), arrowstyle='<->,head_width=3,head_length=5', color='#38BDF8', lw=1.8)
    arr1 = FancyArrowPatch((4.15, 4.3), (3.6, 3.7), arrowstyle='<->,head_width=3,head_length=5', color='#38BDF8', lw=1.8)
    ax.add_patch(arr0)
    ax.add_patch(arr1)

    # Shared L3 Cache Node 0
    l3_0 = FancyBboxPatch((1.0, 2.9), 4.0, 0.8, boxstyle="round,pad=0.1", fc='#1E3A8A', ec='#60A5FA', lw=1.8)
    ax.add_patch(l3_0)
    ax.text(3.0, 3.3, "Shared L3 Cache (20 MB)", color='#FFFFFF', fontsize=11, fontweight='bold', ha='center')

    # Arrow from L3 to Memory Controller
    arr_l3_0 = FancyArrowPatch((3.0, 2.8), (3.0, 2.3), arrowstyle='<->,head_width=3,head_length=5', color='#38BDF8', lw=2)
    ax.add_patch(arr_l3_0)

    # Local Memory RAM 0
    ram0 = FancyBboxPatch((1.0, 1.0), 4.0, 1.2, boxstyle="round,pad=0.15", fc='#065F46', ec='#34D399', lw=2)
    ax.add_patch(ram0)
    ax.text(3.0, 1.8, "Local RAM (Node 0)", color='#A7F3D0', fontsize=13, fontweight='bold', ha='center')
    ax.text(3.0, 1.35, "Size: 2014 MB | Latency: ~60 ns\nFast Local Memory Access", color='#ECFDF5', fontsize=9.5, ha='center')

    # ================== NUMA NODE 1 (Right) ==================
    # Node 1 Box
    node1_box = FancyBboxPatch((7.6, 0.6), 4.8, 5.7, boxstyle="round,pad=0.2",
                               fc='#1E293B', ec='#F43F5E', lw=2.5)
    ax.add_patch(node1_box)
    ax.text(10.0, 6.0, "NUMA NODE 1 (Socket 1)", color='#FB7185', fontsize=14, fontweight='bold', ha='center')

    # Core 2 Box
    c2 = FancyBboxPatch((7.9, 4.4), 1.9, 1.2, boxstyle="round,pad=0.1", fc='#0F172A', ec='#64748B', lw=1.5)
    ax.add_patch(c2)
    ax.text(8.85, 5.2, "Core 2", color='#F8FAFC', fontsize=12, fontweight='bold', ha='center')
    ax.text(8.85, 4.75, "L1 / L2 Cache\n(32KB / 1.25MB)", color='#94A3B8', fontsize=8.5, ha='center')

    # Core 3 Box
    c3 = FancyBboxPatch((10.2, 4.4), 1.9, 1.2, boxstyle="round,pad=0.1", fc='#0F172A', ec='#64748B', lw=1.5)
    ax.add_patch(c3)
    ax.text(11.15, 5.2, "Core 3", color='#F8FAFC', fontsize=12, fontweight='bold', ha='center')
    ax.text(11.15, 4.75, "L1 / L2 Cache\n(32KB / 1.25MB)", color='#94A3B8', fontsize=8.5, ha='center')

    # Arrows from cores to L3
    arr2 = FancyArrowPatch((8.85, 4.3), (9.4, 3.7), arrowstyle='<->,head_width=3,head_length=5', color='#FB7185', lw=1.8)
    arr3 = FancyArrowPatch((11.15, 4.3), (10.6, 3.7), arrowstyle='<->,head_width=3,head_length=5', color='#FB7185', lw=1.8)
    ax.add_patch(arr2)
    ax.add_patch(arr3)

    # Shared L3 Cache Node 1
    l3_1 = FancyBboxPatch((8.0, 2.9), 4.0, 0.8, boxstyle="round,pad=0.1", fc='#881337', ec='#F43F5E', lw=1.8)
    ax.add_patch(l3_1)
    ax.text(10.0, 3.3, "Shared L3 Cache (20 MB)", color='#FFFFFF', fontsize=11, fontweight='bold', ha='center')

    # Arrow from L3 to Memory Controller
    arr_l3_1 = FancyArrowPatch((10.0, 2.8), (10.0, 2.3), arrowstyle='<->,head_width=3,head_length=5', color='#FB7185', lw=2)
    ax.add_patch(arr_l3_1)

    # Remote Memory RAM 1
    ram1 = FancyBboxPatch((8.0, 1.0), 4.0, 1.2, boxstyle="round,pad=0.15", fc='#831843', ec='#FB7185', lw=2)
    ax.add_patch(ram1)
    ax.text(10.0, 1.8, "Remote RAM (Node 1)", color='#FECDD3', fontsize=13, fontweight='bold', ha='center')
    ax.text(10.0, 1.35, "Size: 1902 MB | Latency: ~140 ns\nCross-Socket Remote Access", color='#FFF1F2', fontsize=9.5, ha='center')

    # ================== INTERCONNECT BUS (Center) ==================
    inter_box = FancyBboxPatch((5.55, 1.8), 1.9, 3.0, boxstyle="round,pad=0.15", fc='#312E81', ec='#818CF8', lw=2)
    ax.add_patch(inter_box)
    ax.text(6.5, 4.2, "INTERCONNECT", color='#C7D2FE', fontsize=10, fontweight='bold', ha='center')
    ax.text(6.5, 3.7, "Intel UPI /\nInfinity Fabric", color='#FFFFFF', fontsize=11, fontweight='bold', ha='center')
    ax.text(6.5, 2.8, "Inter-Socket Link\nDistance: 20\n(vs Local 10)", color='#A5B4FC', fontsize=9, ha='center')

    # Arrows connecting Node 0 & Node 1 through Interconnect
    conn_left = FancyArrowPatch((5.1, 3.3), (5.5, 3.3), arrowstyle='<->,head_width=4,head_length=6', color='#818CF8', lw=2.5)
    conn_right = FancyArrowPatch((7.5, 3.3), (7.9, 3.3), arrowstyle='<->,head_width=4,head_length=6', color='#818CF8', lw=2.5)
    ax.add_patch(conn_left)
    ax.add_patch(conn_right)

    plt.tight_layout()
    plt.savefig("images/numa_architecture.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[+] Created images/numa_architecture.png")


def create_false_sharing_diagram():
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    # Main Title
    ax.text(6.5, 8.0, "False Sharing vs Padded Cache Line Layout",
            ha='center', va='center', color='#F8FAFC', fontsize=18, fontweight='bold')
    ax.text(6.5, 7.6, "How 64-Byte Cache Granularity Destroys vs Preserves Multi-Threaded Scalability",
            ha='center', va='center', color='#94A3B8', fontsize=11)

    # ================= TOP SECTION: ADJACENT LAYOUT =================
    adj_box = FancyBboxPatch((0.5, 4.3), 12.0, 3.0, boxstyle="round,pad=0.2",
                             fc='#1E293B', ec='#EF4444', lw=2)
    ax.add_patch(adj_box)
    ax.text(1.0, 7.0, "ADJACENT LAYOUT (64-byte Cache Line Shared by Core 0 & Core 1) -> FALSE SHARING",
            color='#F87171', fontsize=12, fontweight='bold')

    # Cache line bar
    # 64 bytes total width = 10 units
    # x = 8 bytes = 1.25 units
    # y = 8 bytes = 1.25 units
    # remainder = 48 bytes = 7.5 units
    bar_x = 1.5
    bar_y = 5.6
    bar_h = 0.8

    # Block x
    bx = FancyBboxPatch((bar_x, bar_y), 1.25, bar_h, boxstyle="square,pad=0", fc='#38BDF8', ec='#0284C7', lw=1.5)
    ax.add_patch(bx)
    ax.text(bar_x + 0.625, bar_y + 0.4, "x (8B)", color='#0F172A', fontsize=10, fontweight='bold', ha='center', va='center')

    # Block y
    by = FancyBboxPatch((bar_x + 1.25, bar_y), 1.25, bar_h, boxstyle="square,pad=0", fc='#FB923C', ec='#EA580C', lw=1.5)
    ax.add_patch(by)
    ax.text(bar_x + 1.875, bar_y + 0.4, "y (8B)", color='#0F172A', fontsize=10, fontweight='bold', ha='center', va='center')

    # Remaining 48B
    br = FancyBboxPatch((bar_x + 2.5, bar_y), 7.5, bar_h, boxstyle="square,pad=0", fc='#334155', ec='#475569', lw=1.5)
    ax.add_patch(br)
    ax.text(bar_x + 6.25, bar_y + 0.4, "Unused Cache Line Space (48 Bytes)", color='#94A3B8', fontsize=10, ha='center', va='center')

    # Offset markers
    ax.text(bar_x, bar_y + 0.95, "Byte 0", color='#94A3B8', fontsize=8, ha='center')
    ax.text(bar_x + 1.25, bar_y + 0.95, "Byte 8", color='#94A3B8', fontsize=8, ha='center')
    ax.text(bar_x + 2.5, bar_y + 0.95, "Byte 16", color='#94A3B8', fontsize=8, ha='center')
    ax.text(bar_x + 10.0, bar_y + 0.95, "Byte 64", color='#94A3B8', fontsize=8, ha='center')

    # Cores operating
    ax.text(bar_x + 0.625, bar_y - 0.35, "Core 0\n[Writes x]", color='#38BDF8', fontsize=9.5, fontweight='bold', ha='center')
    ax.text(bar_x + 1.875, bar_y - 0.35, "Core 1\n[Writes y]", color='#FB923C', fontsize=9.5, fontweight='bold', ha='center')

    # Ping-Pong explanation box
    pp_box = FancyBboxPatch((4.5, 4.6), 7.5, 0.85, boxstyle="round,pad=0.1", fc='#7F1D1D', ec='#EF4444', lw=1.5)
    ax.add_patch(pp_box)
    ax.text(8.25, 5.15, "SEVERE PING-PONG EFFECT (Bus Storm)", color='#FCA5A5', fontsize=10, fontweight='bold', ha='center')
    ax.text(8.25, 4.8, "Every write by Core 0 INVALIDATES Core 1's entire 64B line & vice-versa!\nExecution stalled waiting for cache invalidations (0.0142s at 2T).",
            color='#FEE2E2', fontsize=8.5, ha='center')

    # ================= BOTTOM SECTION: PADDED LAYOUT =================
    pad_box = FancyBboxPatch((0.5, 0.5), 12.0, 3.4, boxstyle="round,pad=0.2",
                             fc='#1E293B', ec='#10B981', lw=2)
    ax.add_patch(pad_box)
    ax.text(1.0, 3.6, "PADDED LAYOUT (Each Counter Aligned to Its Own 64-Byte Cache Line) -> ZERO CONFLICT",
            color='#34D399', fontsize=12, fontweight='bold')

    # Line A
    la_y = 2.4
    la_x = FancyBboxPatch((bar_x, la_y), 1.25, 0.65, boxstyle="square,pad=0", fc='#38BDF8', ec='#0284C7', lw=1.5)
    ax.add_patch(la_x)
    ax.text(bar_x + 0.625, la_y + 0.325, "x (8B)", color='#0F172A', fontsize=9.5, fontweight='bold', ha='center', va='center')

    la_pad = FancyBboxPatch((bar_x + 1.25, la_y), 8.75, 0.65, boxstyle="square,pad=0", fc='#064E3B', ec='#059669', lw=1.2)
    ax.add_patch(la_pad)
    ax.text(bar_x + 5.6, la_y + 0.325, "64-Byte Cache Line A Padding (56 Bytes)  ->  Line A isolated to Core 0",
            color='#A7F3D0', fontsize=9.5, ha='center', va='center')

    # Line B
    lb_y = 1.3
    lb_pad0 = FancyBboxPatch((bar_x, lb_y), 1.25, 0.65, boxstyle="square,pad=0", fc='#334155', ec='#475569', lw=1.2)
    ax.add_patch(lb_pad0)
    ax.text(bar_x + 0.625, lb_y + 0.325, "Stride Offset", color='#94A3B8', fontsize=8, ha='center', va='center')

    lb_y_box = FancyBboxPatch((bar_x + 1.25, lb_y), 1.25, 0.65, boxstyle="square,pad=0", fc='#FB923C', ec='#EA580C', lw=1.5)
    ax.add_patch(lb_y_box)
    ax.text(bar_x + 1.875, lb_y + 0.325, "y (8B)", color='#0F172A', fontsize=9.5, fontweight='bold', ha='center', va='center')

    lb_pad1 = FancyBboxPatch((bar_x + 2.5, lb_y), 7.5, 0.65, boxstyle="square,pad=0", fc='#064E3B', ec='#059669', lw=1.2)
    ax.add_patch(lb_pad1)
    ax.text(bar_x + 6.25, lb_y + 0.325, "64-Byte Cache Line B Padding (56 Bytes)  ->  Line B isolated to Core 1",
            color='#A7F3D0', fontsize=9.5, ha='center', va='center')

    # Scalability note
    ax.text(6.5, 0.75, "RESULTS: Zero Bus Invalidations  |  Each Core writes locally in Modified ('M') state  |  Up to 21.5x Speedup!",
            color='#6EE7B7', fontsize=10.5, fontweight='bold', ha='center')

    plt.tight_layout()
    plt.savefig("images/false_sharing_diagram.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[+] Created images/false_sharing_diagram.png")

if __name__ == '__main__':
    create_numa_diagram()
    create_false_sharing_diagram()

def create_coherence_snooping_diagram():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')

    # Title
    ax.text(6.0, 6.0, "Hardware Snooping Cache Coherence Architecture",
            ha='center', va='center', color='#F8FAFC', fontsize=17, fontweight='bold')
    ax.text(6.0, 5.6, "How Cores Monitor Shared Interconnect to Maintain Memory Consistency",
            ha='center', va='center', color='#94A3B8', fontsize=11)

    # Core 0 Box
    c0 = FancyBboxPatch((1.2, 3.4), 3.8, 1.8, boxstyle="round,pad=0.15", fc='#1E293B', ec='#38BDF8', lw=2)
    ax.add_patch(c0)
    ax.text(3.1, 4.8, "Processor Core 0", color='#38BDF8', fontsize=13, fontweight='bold', ha='center')
    l1_0 = FancyBboxPatch((1.5, 3.6), 3.2, 0.9, boxstyle="round,pad=0.1", fc='#0F172A', ec='#64748B', lw=1.2)
    ax.add_patch(l1_0)
    ax.text(3.1, 4.15, "Private L1 Data Cache", color='#F8FAFC', fontsize=10, fontweight='bold', ha='center')
    ax.text(3.1, 3.8, "Line A: State = [ Modified 'M' ]", color='#FBBF24', fontsize=9.5, ha='center')

    # Core 1 Box
    c1 = FancyBboxPatch((7.0, 3.4), 3.8, 1.8, boxstyle="round,pad=0.15", fc='#1E293B', ec='#F43F5E', lw=2)
    ax.add_patch(c1)
    ax.text(8.9, 4.8, "Processor Core 1", color='#FB7185', fontsize=13, fontweight='bold', ha='center')
    l1_1 = FancyBboxPatch((7.3, 3.6), 3.2, 0.9, boxstyle="round,pad=0.1", fc='#0F172A', ec='#64748B', lw=1.2)
    ax.add_patch(l1_1)
    ax.text(8.9, 4.15, "Private L1 Data Cache", color='#F8FAFC', fontsize=10, fontweight='bold', ha='center')
    ax.text(8.9, 3.8, "Line A: State = [ Invalid 'I' ]", color='#EF4444', fontsize=9.5, ha='center')

    # Snooping Bus
    bus = FancyBboxPatch((0.8, 2.0), 10.4, 0.75, boxstyle="round,pad=0.1", fc='#312E81', ec='#818CF8', lw=2.2)
    ax.add_patch(bus)
    ax.text(6.0, 2.38, "SHARED SNOOPING BUS / COHERENCE INTERCONNECT", color='#FFFFFF', fontsize=11.5, fontweight='bold', ha='center')

    # Bus snooping arrows
    snoop0 = FancyArrowPatch((3.1, 3.4), (3.1, 2.75), arrowstyle='<->,head_width=4,head_length=6', color='#38BDF8', lw=2.5)
    snoop1 = FancyArrowPatch((8.9, 3.4), (8.9, 2.75), arrowstyle='<->,head_width=4,head_length=6', color='#FB7185', lw=2.5)
    ax.add_patch(snoop0)
    ax.add_patch(snoop1)

    ax.text(2.2, 3.05, "Snoop & Broadcast", color='#38BDF8', fontsize=8.5, ha='center', style='italic')
    ax.text(9.8, 3.05, "Snoop & Invalidate", color='#FB7185', fontsize=8.5, ha='center', style='italic')

    # Main Memory RAM
    ram = FancyBboxPatch((3.5, 0.4), 5.0, 1.0, boxstyle="round,pad=0.15", fc='#065F46', ec='#34D399', lw=2)
    ax.add_patch(ram)
    ax.text(6.0, 1.05, "Shared Main Memory (DRAM)", color='#A7F3D0', fontsize=12, fontweight='bold', ha='center')
    ax.text(6.0, 0.65, "Line A: [ Memory Backed Value ]", color='#ECFDF5', fontsize=9.5, ha='center')

    # Bus to RAM arrow
    ram_conn = FancyArrowPatch((6.0, 2.0), (6.0, 1.4), arrowstyle='<->,head_width=4,head_length=6', color='#34D399', lw=2.5)
    ax.add_patch(ram_conn)

    plt.tight_layout()
    plt.savefig("images/cache_coherence_snooping.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[+] Created images/cache_coherence_snooping.png")
