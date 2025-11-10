"""
Compare caches on a specially-crafted hybrid workload that alternates
between frequency-dominated phases and recency (one-shot) bursts.

This workload is designed to show Adaptive ARC's advantage: it can
adapt between keeping frequently-used items and temporarily favoring
recent items during scanning bursts, thereby achieving a higher
overall hit rate than pure LRU/LFU/FIFO on this pattern.

Run: python3 demo_compare.py
"""

import time
import random

from demo_adaptive_arc import AdaptiveARCCache
from demo_lru import LRUCache
from demo_lfu import LFUCache
from demo_fifo import FIFOCache


def generate_hybrid_workload(cycles=40, hot_size=20, hot_accesses=50, burst_size=50, start_unique=10000, rotate_every=8, rotate_shift=50):
    """
    Create a workload that repeats the following pattern:
      - hot_accesses accesses randomly drawn from a small hot set (build frequency)
      - burst_size unique accesses (one-shot recency scan)

    cycles: number of repetition cycles
    hot_size: size of the hot (frequently reused) set
    hot_accesses: number of accesses in the frequency phase
    burst_size: number of unique one-shot items in the recency burst
    start_unique: starting integer for generating unique keys
    """
    workload = []
    base_hot = 0
    hot_set = list(range(base_hot, base_hot + hot_size))
    unique_id = start_unique

    for c in range(cycles):
        # Occasionally rotate the hot set to simulate changing 'popular' items
        if rotate_every and c % rotate_every == 0 and c > 0:
            base_hot += rotate_shift
            hot_set = list(range(base_hot, base_hot + hot_size))

        # Frequency phase: many accesses to the hot set
        for _ in range(hot_accesses):
            workload.append(random.choice(hot_set))

        # Recency burst: many unique items each seen once
        for _ in range(burst_size):
            workload.append(unique_id)
            unique_id += 1

    return workload


def run_on_cache(cache, workload):
    """Run workload on a cache object implementing get/put and stats tracking."""
    # Clear if available
    try:
        cache.clear()
    except Exception:
        pass

    start = time.time()
    for key in workload:
        val = cache.get(key)
        if val is None:
            cache.put(key, f"value_{key}")
    duration = (time.time() - start) * 1000.0
    # Try to get stats
    try:
        stats = cache.get_stats()
    except Exception:
        stats = {
            'algorithm': cache.__class__.__name__,
            'capacity': getattr(cache, 'capacity', None),
            'accesses': getattr(cache, 'access_count', None),
            'hits': getattr(cache, 'hit_count', None),
            'hit_rate': getattr(cache, 'get_hit_rate', lambda: None)(),
        }

    stats['runtime_ms'] = duration
    return stats


def pretty_print_results(results):
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)
    for r in results:
        print(f"Algorithm: {r['algorithm']:15} | Hit Rate: {r['hit_rate']:.2%} | Hits: {r.get('hits', '?'):6} | Accesses: {r.get('accesses', '?'):6} | Runtime: {r['runtime_ms']:.2f} ms")


def main():
    # Tunable parameters
    cache_capacity = 50
    cycles = 40
    hot_size = 20
    hot_accesses = 50
    burst_size = 50

    workload = generate_hybrid_workload(cycles=cycles, hot_size=hot_size, hot_accesses=hot_accesses, burst_size=burst_size)

    print(f"Workload: cycles={cycles}, hot_size={hot_size}, hot_accesses={hot_accesses}, burst_size={burst_size}, total_accesses={len(workload)}")

    # Create caches
    arc = AdaptiveARCCache(capacity=cache_capacity)
    lru = LRUCache(capacity=cache_capacity)
    lfu = LFUCache(capacity=cache_capacity)
    fifo = FIFOCache(capacity=cache_capacity)

    results = []
    for cache in (arc, lru, lfu, fifo):
        stats = run_on_cache(cache, workload)
        results.append(stats)

    # Sort by hit rate desc
    results.sort(key=lambda r: r.get('hit_rate', 0.0), reverse=True)
    pretty_print_results(results)

    # Indicate winner
    winner = results[0]
    print("\nWinner: {} with hit rate {:.2%}".format(winner['algorithm'], winner['hit_rate']))


if __name__ == '__main__':
    main()
