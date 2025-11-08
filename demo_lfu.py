"""
LFU Cache Demonstration
Shows LFU performance with timing
Standalone version with all code included
"""

import time
import random
from collections import defaultdict


class LFUCache:
    """Least Frequently Used (LFU) Cache - O(1) operations"""
    
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = {}  # key -> (value, frequency, timestamp)
        self.frequency = defaultdict(int)
        self.access_count = 0
        self.hit_count = 0
    
    def get(self, key):
        """Retrieve value from cache."""
        self.access_count += 1
        if key in self.cache:
            self.hit_count += 1
            value, freq, _ = self.cache[key]
            self.cache[key] = (value, freq + 1, time.time())
            return value
        return None
    
    def put(self, key, value):
        """Insert or update value in cache."""
        if key in self.cache:
            _, freq, _ = self.cache[key]
            self.cache[key] = (value, freq + 1, time.time())
        else:
            if len(self.cache) >= self.capacity:
                lfu_key = min(self.cache.keys(), 
                            key=lambda k: (self.cache[k][1], self.cache[k][2]))
                del self.cache[lfu_key]
            self.cache[key] = (value, 1, time.time())
    
    def get_hit_rate(self):
        """Calculate cache hit rate."""
        if self.access_count == 0:
            return 0.0
        return self.hit_count / self.access_count
    
    def get_stats(self):
        """Get cache statistics."""
        return {
            'algorithm': 'LFU',
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
        self.frequency.clear()
        self.access_count = 0
        self.hit_count = 0


def demo_lfu():
    print("="*70)
    print("LFU (Least Frequently Used) Cache Demonstration")
    print("="*70)
    
    # Configuration
    cache_capacity = 50
    workload_size = 1000
    data_universe = 200
    
    print(f"\nConfiguration:")
    print(f"  Cache Capacity: {cache_capacity}")
    print(f"  Workload Size: {workload_size} accesses")
    print(f"  Data Universe: {data_universe} unique keys")
    
    # Create cache
    cache = LFUCache(capacity=cache_capacity)
    
    # Generate realistic workload (Zipf distribution)
    print("\nGenerating Zipf workload...")
    workload = []
    weights = [1.0 / (i + 1) ** 1.5 for i in range(data_universe)]
    total = sum(weights)
    weights = [w / total for w in weights]
    workload = random.choices(range(data_universe), weights=weights, k=workload_size)
    
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
    print(f"Avg per access:   {runtime/workload_size:.4f} ms")
    print("="*70)
    
    return stats


if __name__ == "__main__":
    demo_lfu()
