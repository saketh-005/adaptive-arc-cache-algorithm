"""
FIFO Cache Demonstration
Shows FIFO performance with timing
Standalone version with all code included
"""

import time
import random
from collections import OrderedDict


class FIFOCache:
    """First In First Out (FIFO) Cache - O(1) operations"""
    
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = OrderedDict()
        self.access_count = 0
        self.hit_count = 0
    
    def get(self, key):
        """Retrieve value from cache."""
        self.access_count += 1
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        return None
    
    def put(self, key, value):
        """Insert or update value in cache."""
        if key in self.cache:
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def get_hit_rate(self):
        """Calculate cache hit rate."""
        if self.access_count == 0:
            return 0.0
        return self.hit_count / self.access_count
    
    def get_stats(self):
        """Get cache statistics."""
        return {
            'algorithm': 'FIFO',
            'capacity': self.capacity,
            'size': len(self.cache),
            'accesses': self.access_count,
            'hits': self.hit_count,
            'misses': self.access_count - self.hit_count,
            'hit_rate': self.get_hit_rate()
        }
    
    def clear(self):
        """Clear cache and reset statistics."""
        self.cache.clear()
        self.access_count = 0
        self.hit_count = 0


def demo_fifo():
    print("="*70)
    print("FIFO (First In First Out) Cache Demonstration")
    print("="*70)
    
    # Configuration — use the hybrid workload (frequency phases + recency bursts)
    cache_capacity = 50
    cycles = 40
    hot_size = 20
    hot_accesses = 50
    burst_size = 50

    print(f"\nConfiguration:")
    print(f"  Cache Capacity: {cache_capacity}")
    print(f"  Workload: cycles={cycles}, hot_size={hot_size}, hot_accesses={hot_accesses}, burst_size={burst_size}")

    # Create cache
    cache = FIFOCache(capacity=cache_capacity)

    # Hybrid workload generator (local copy)
    def generate_hybrid_workload(cycles=40, hot_size=20, hot_accesses=50, burst_size=50, start_unique=10000, rotate_every=8, rotate_shift=50):
        workload = []
        base_hot = 0
        hot_set = list(range(base_hot, base_hot + hot_size))
        unique_id = start_unique

        for c in range(cycles):
            if rotate_every and c % rotate_every == 0 and c > 0:
                base_hot += rotate_shift
                hot_set = list(range(base_hot, base_hot + hot_size))

            for _ in range(hot_accesses):
                workload.append(random.choice(hot_set))

            for _ in range(burst_size):
                workload.append(unique_id)
                unique_id += 1

        return workload

    workload = generate_hybrid_workload(cycles=cycles, hot_size=hot_size, hot_accesses=hot_accesses, burst_size=burst_size)
    
    # Run test
    print("Running test...")
    start_time = time.time()
    
    for key in workload:
        result = cache.get(key)
        if result is None:
            # Cache miss - fetch and store
            cache.put(key, f"value_{key}")
    
    end_time = time.time()
    runtime = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Results
    stats = cache.get_stats()
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Algorithm:        {stats['algorithm']}")
    print(f"Cache Size:       {stats['size']}/{stats['capacity']}")
    print(f"Total Accesses:   {stats['accesses']}")
    print(f"Cache Hits:       {stats['hits']}")
    print(f"Cache Misses:     {stats['misses']}")
    print(f"Hit Rate:         {stats['hit_rate']:.2%}")
    print(f"Runtime:          {runtime:.2f} ms")
    print(f"Avg per access:   {runtime/len(workload):.4f} ms")
    print("="*70)
    
    return stats


if __name__ == "__main__":
    demo_fifo()
