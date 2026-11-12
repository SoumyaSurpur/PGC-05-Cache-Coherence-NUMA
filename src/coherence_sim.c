/*
 * ============================================================================
 * Experiment 5: Cache Coherence Protocol Simulator (MSI, MESI, MOESI)
 * File: coherence_sim.c
 * Course: Parallel and GPU Computing (PGC)
 * Author: Soumya Surpur (USN: 01FE24BCI121)
 * Institution: KLE Technological University
 *
 * Description:
 *   Simulates a 2-core snooping cache system executing read/write memory traces
 *   under three industry-standard cache coherence protocols:
 *     1. MSI   (Baseline invalidation protocol)
 *     2. MESI  (Adds Exclusive state to optimize private data writes)
 *     3. MOESI (Adds Owned state to enable dirty cache-to-cache data transfers)
 *
 *   Evaluates memory layouts:
 *     - Adjacent: Counters x and y reside on the SAME 64-byte cache line (Line A).
 *                 Produces massive coherence traffic due to False Sharing.
 *     - Padded:   Counters x and y reside on SEPARATE cache lines (Line A & B).
 *                 Eliminates coherence invalidations completely.
 *
 * Compilation:
 *   gcc -O2 coherence_sim.c -o coherence_sim
 *
 * Execution:
 *   ./coherence_sim [iterations]
 *   Default iterations: 1000 (4000 memory operations)
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_CORES 2
#define MAX_LINES 2

/* Cache Line States */
typedef enum {
    STATE_I = 0, /* Invalid */
    STATE_S,     /* Shared */
    STATE_M,     /* Modified */
    STATE_E,     /* Exclusive (MESI, MOESI) */
    STATE_O      /* Owned (MOESI) */
} CacheState;

const char *state_to_str(CacheState s) {
    switch (s) {
        case STATE_I: return "I";
        case STATE_S: return "S";
        case STATE_M: return "M";
        case STATE_E: return "E";
        case STATE_O: return "O";
        default: return "?";
    }
}

typedef enum {
    PROTO_MSI = 0,
    PROTO_MESI,
    PROTO_MOESI
} Protocol;

const char *proto_to_str(Protocol p) {
    switch (p) {
        case PROTO_MSI:   return "MSI";
        case PROTO_MESI:  return "MESI";
        case PROTO_MOESI: return "MOESI";
        default: return "UNKNOWN";
    }
}

/* Statistics tracking structure */
typedef struct {
    long bus_rd;
    long bus_rdx;
    long bus_upgr;
    long silent_e_m;
    long invalidations;
    long writeback;
    long c2c;
    long bus_transactions;
} Stats;

/* Simulate single cache access (Read 'R' or Write 'W') */
void access_cache(Protocol proto, CacheState caches[MAX_CORES][MAX_LINES],
                  int core, int line, char op, Stats *st) {
    CacheState s = caches[core][line];
    int other = 1 - core;
    int other_holds = (caches[other][line] != STATE_I);

    if (op == 'R') {
        /* Read Operation */
        if (s != STATE_I) {
            return; /* Read hit: zero bus traffic */
        }

        st->bus_rd++;
        CacheState new_state = STATE_S;

        if (other_holds) {
            CacheState o = caches[other][line];
            if (o == STATE_M) {
                if (proto == PROTO_MOESI) {
                    /* MOESI: Owner keeps dirty line as Owned, sends data via C2C */
                    caches[other][line] = STATE_O;
                    st->c2c++;
                } else {
                    /* MSI/MESI: Line must be flushed to main memory */
                    caches[other][line] = STATE_S;
                    st->writeback++;
                }
            } else if (o == STATE_O) {
                /* In MOESI, the Owned cache supplies data directly */
                st->c2c++;
            } else if (o == STATE_E) {
                caches[other][line] = STATE_S;
            }
        }

        /* If no other cache has a copy, MESI/MOESI load into Exclusive state */
        if (!other_holds && (proto == PROTO_MESI || proto == PROTO_MOESI)) {
            new_state = STATE_E;
        }
        caches[core][line] = new_state;

    } else if (op == 'W') {
        /* Write Operation */
        if (s == STATE_M) {
            return; /* Write hit on Modified line: zero bus traffic */
        }

        if (s == STATE_E) {
            /* Silent transition: E -> M requires no bus transaction! */
            caches[core][line] = STATE_M;
            st->silent_e_m++;
            return;
        }

        if (s == STATE_S || s == STATE_O) {
            /* Line already present: issue Upgrade broadcast */
            st->bus_upgr++;
        } else {
            /* Line Invalid: issue Read-For-Ownership (BusRdX) */
            st->bus_rdx++;
            if (other_holds) {
                CacheState o = caches[other][line];
                if (o == STATE_M || o == STATE_O) {
                    if (proto == PROTO_MOESI) {
                        st->c2c++;
                    } else {
                        st->writeback++;
                    }
                }
            }
        }

        /* Invalidate other core's cache line */
        if (other_holds) {
            caches[other][line] = STATE_I;
            st->invalidations++;
        }
        caches[core][line] = STATE_M;
    }
}

/* Run simulation for a specific protocol and layout */
Stats run_simulation(Protocol proto, const char *layout, int iters, int print_trace) {
    Stats st = {0};
    CacheState caches[MAX_CORES][MAX_LINES];
    for (int c = 0; c < MAX_CORES; c++) {
        for (int l = 0; l < MAX_LINES; l++) {
            caches[c][l] = STATE_I;
        }
    }

    /* Adjacent: both line 0 (Line A). Padded: x is line 0, y is line 1 */
    int lx = 0;
    int ly = (strcmp(layout, "adjacent") == 0) ? 0 : 1;

    for (int it = 0; it < iters; it++) {
        /* Workload trace: Core 0 R/W x, then Core 1 R/W y */
        struct { int core; int line; char op; } trace[4] = {
            {0, lx, 'R'},
            {0, lx, 'W'},
            {1, ly, 'R'},
            {1, ly, 'W'}
        };

        for (int i = 0; i < 4; i++) {
            access_cache(proto, caches, trace[i].core, trace[i].line, trace[i].op, &st);
            if (print_trace) {
                printf(" core%d %c -> C0=%s C1=%s\n",
                       trace[i].core, trace[i].op,
                       state_to_str(caches[0][0]),
                       state_to_str(caches[1][0]));
            }
        }
    }

    st.bus_transactions = st.bus_rd + st.bus_rdx + st.bus_upgr;
    return st;
}

int main(int argc, char **argv) {
    int iters = (argc > 1) ? atoi(argv[1]) : 1000;

    printf("State trace, first 2 iterations, adjacent layout (line A: core0 state / core1 state)\n");

    Protocol protos[3] = {PROTO_MSI, PROTO_MESI, PROTO_MOESI};

    for (int p = 0; p < 3; p++) {
        printf("\n%s:\n", proto_to_str(protos[p]));
        run_simulation(protos[p], "adjacent", 2, 1);
    }

    printf("\nTotals for %d iterations\n", iters);
    printf("%-9s %-6s %16s %16s %16s %16s %16s %16s %16s %16s\n",
           "layout", "protocol", "bus transactions", "BusRd", "BusRdX", "BusUpgr",
           "invalidations", "writeback", "c2c", "silent E->M");

    const char *layouts[2] = {"adjacent", "padded"};

    for (int l = 0; l < 2; l++) {
        for (int p = 0; p < 3; p++) {
            Stats st = run_simulation(protos[p], layouts[l], iters, 0);
            printf("%-9s %-6s %16ld %16ld %16ld %16ld %16ld %16ld %16ld %16ld\n",
                   layouts[l], proto_to_str(protos[p]),
                   st.bus_transactions, st.bus_rd, st.bus_rdx, st.bus_upgr,
                   st.invalidations, st.writeback, st.c2c, st.silent_e_m);
        }
    }

    return 0;
}
