#!/usr/bin/env python3
"""
================================================================================
Experiment 5: Cache Coherence (MSI, MESI, MOESI) Protocol Simulator
Course: Parallel and GPU Computing (PGC)
Author: Soumya Surpur (USN: 01FE24BCI121)
Institution: KLE Technological University

Description:
  A 2-core snooping-cache coherence simulator comparing MSI, MESI, and MOESI
  protocols under two distinct memory layouts:
  1. Adjacent Layout: Variables x and y share the SAME cache line 'A' (False Sharing).
  2. Padded Layout: Variables x and y reside on SEPARATE cache lines 'A' and 'B'.

Workload:
  Core 0 performs: x = x + 1 (Read x, Write x)
  Core 1 performs: y = y + 1 (Read y, Write y)
  Repeated for N iterations (default 1000 iterations = 4000 memory operations).
================================================================================
"""

import sys

def make_cores(n=2):
    """Initializes empty caches for n processor cores."""
    return [dict() for _ in range(n)]

def access(proto, caches, core, line, op, st):
    """
    Executes a memory access (Read 'R' or Write 'W') by a specific core on a cache line.
    Updates the cache states across cores according to the snooping coherence protocol
    (MSI, MESI, or MOESI) and increments hardware event statistics in dict st.
    """
    me = caches[core]
    s = me.get(line, 'I')
    others = [i for i in range(len(caches)) if i != core]
    holders = [i for i in others if caches[i].get(line, 'I') != 'I']

    if op == 'R':  # READ Operation
        if s != 'I':
            return  # Cache Read Hit: no bus activity required

        st['BusRd'] += 1
        new = 'S'

        for i in holders:
            o = caches[i][line]
            if o == 'M':
                if proto == 'MOESI':
                    # MOESI Optimization: Line transitions to Owned (O).
                    # The owner serves data directly via cache-to-cache transfer.
                    # Memory is NOT updated now, saving a costly memory write-back!
                    caches[i][line] = 'O'
                    st['c2c'] += 1
                else:
                    # MSI & MESI: Modified line must write back to memory before sharing.
                    caches[i][line] = 'S'
                    st['writeback'] += 1
            elif o == 'O':
                # MOESI: Owner continues to supply data to other reading cores.
                st['c2c'] += 1
            elif o == 'E':
                caches[i][line] = 'S'

        # MESI & MOESI Optimization: If no other cache holds the line, load as Exclusive (E).
        if not holders and proto in ('MESI', 'MOESI'):
            new = 'E'
        me[line] = new

    else:  # WRITE Operation
        if s == 'M':
            return  # Cache Write Hit in Modified state: no bus transaction needed

        if s == 'E':
            # MESI & MOESI Silent Transition: E -> M requires NO bus transaction
            # because this cache already possesses the exclusive clean copy.
            me[line] = 'M'
            st['silent E->M'] += 1
            return

        if s in ('S', 'O'):
            # Line is shared: core issues BusUpgr (upgrade) to invalidate remote copies.
            st['BusUpgr'] += 1
        else:  # s == 'I'
            # Write miss: core must issue BusRdX (Read-For-Ownership)
            st['BusRdX'] += 1
            for i in holders:
                o = caches[i][line]
                if o in ('M', 'O'):
                    if proto == 'MOESI':
                        st['c2c'] += 1
                    else:
                        st['writeback'] += 1

        # Invalidate copies in all other caches
        for i in holders:
            caches[i][line] = 'I'
            st['invalidations'] += 1
        me[line] = 'M'

def run(proto, layout, iters):
    """Simulates protocol execution over specified iterations and layout."""
    st = dict.fromkeys([
        'BusRd', 'BusRdX', 'BusUpgr', 'silent E->M',
        'invalidations', 'writeback', 'c2c'
    ], 0)
    caches = make_cores()

    # In adjacent layout, both variables map to line 'A'.
    # In padded layout, x maps to 'A' and y maps to 'B'.
    lx, ly = ('A', 'A') if layout == 'adjacent' else ('A', 'B')

    trace = []
    for _ in range(iters):
        trace += [(0, lx, 'R'), (0, lx, 'W'), (1, ly, 'R'), (1, ly, 'W')]

    log = []
    for core, line, op in trace:
        access(proto, caches, core, line, op, st)
        log.append((core, line, op, caches[0].get('A', 'I'), caches[1].get('A', 'I')))

    st['bus transactions'] = st['BusRd'] + st['BusRdX'] + st['BusUpgr']
    return st, log

if __name__ == '__main__':
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    print("State trace, first 2 iterations, adjacent layout (line A: core0 state / core1 state)")
    for proto in ('MSI', 'MESI', 'MOESI'):
        _, log = run(proto, 'adjacent', 2)
        print(f"\n{proto}:")
        for c, l, o, s0, s1 in log:
            print(f" core{c} {o} -> C0={s0} C1={s1}")

    print(f"\nTotals for {iters} iterations")
    keys = ['bus transactions', 'BusRd', 'BusRdX', 'BusUpgr', 'invalidations', 'writeback', 'c2c', 'silent E->M']
    print(f"{'layout':9} {'protocol':6} " + " ".join(f"{k:>16}" for k in keys))
    for layout in ('adjacent', 'padded'):
        for proto in ('MSI', 'MESI', 'MOESI'):
            st, _ = run(proto, layout, iters)
            print(f"{layout:9} {proto:6} " + " ".join(f"{st[k]:>16}" for k in keys))
