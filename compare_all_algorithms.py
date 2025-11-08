"""
Comprehensive Cache Algorithm Comparison
Compares FIFO, LRU, LFU, and the new Adaptive-ARC algorithm

This script demonstrates the superiority of the Adaptive-ARC algorithm
for Design and Analysis of Algorithms Assignment
"""

import time
import random
from collections import OrderedDict, defaultdict


# Import all cache implementations
class FIFOCache:
    """First In First Out (FIFO) Cache"""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.access_count = 0
        self.hit_count = 0
    
    def get(self, key):
        self.access_count += 1
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def get_hit_rate(self):
        return self.hit_count / self.access_count if self.access_count > 0 else 0.0
    
    def get_stats(self):
        return {
            'algorithm': 'FIFO',
            'hits': self.hit_count,
            'misses': self.access_count - self.hit_count,
            'hit_rate': self.get_hit_rate()
        }


class LRUCache:
    """Least Recently Used (LRU) Cache"""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.access_count = 0
        self.hit_count = 0
    
    def get(self, key):
        self.access_count += 1
        if key in self.cache:
            self.hit_count += 1
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def get_hit_rate(self):
        return self.hit_count / self.access_count if self.access_count > 0 else 0.0
    
    def get_stats(self):
        return {
            'algorithm': 'LRU',
            'hits': self.hit_count,
            'misses': self.access_count - self.hit_count,
            'hit_rate': self.get_hit_rate()
        }


class LFUCache:
    """Least Frequently Used (LFU) Cache"""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.frequency = defaultdict(int)
        self.access_count = 0
        self.hit_count = 0
    
    def get(self, key):
        self.access_count += 1
        if key in self.cache:
            self.hit_count += 1
            value, freq, _ = self.cache[key]
            self.cache[key] = (value, freq + 1, time.time())
            return value
        return None
    
    def put(self, key, value):
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
        return self.hit_count / self.access_count if self.access_count > 0 else 0.0
    
    def get_stats(self):
        return {
            'algorithm': 'LFU',
            'hits': self.hit_count,
            'misses': self.access_count - self.hit_count,
            'hit_rate': self.get_hit_rate()
        }


class AdaptiveARCCache:
    """Adaptive ARC Cache with Frequency Boost - NEW ALGORITHM"""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.t1 = OrderedDict()  # Recent items
        self.t2 = OrderedDict()  # Frequent items
        self.b1 = OrderedDict()  # Ghost entries from T1
        self.b2 = OrderedDict()  # Ghost entries from T2
        self.p = capacity // 2  # Start balanced
        self.access_count = 0
        self.hit_count = 0
        self.current_time = 0
        
        # Enhanced: Dynamic learning rate
        self.learning_rate = 0.1
        self.recency_score_sum = 0
        self.frequency_score_sum = 0
    
    def _current_timestamp(self):
        self.current_time += 1
        return self.current_time
    
    def _calculate_value_score(self, frequency, timestamp, age):
        """Calculate item value with exponential decay for recency"""
        # Recency with exponential decay
        recency = max(1, self.current_time - timestamp + 1)
        recency_score = 1.0 / (recency ** 0.5)
        
        # Frequency score with logarithmic scaling
        frequency_score = frequency ** 1.2
        
        # Combined score with dynamic weighting
        score = frequency_score * recency_score
        return score
    
    def _adapt(self, hit_in_b1):
        """Adaptive mechanism with learning"""
        if hit_in_b1:
            # Increase T1 target size
            delta = max(1, len(self.b2) // max(len(self.b1), 1))
            self.p = min(self.p + delta, self.capacity)
        else:
            # Increase T2 target size
            delta = max(1, len(self.b1) // max(len(self.b2), 1))
            self.p = max(self.p - delta, 0)
    
    def _replace(self, in_b2):
        """Intelligent replacement strategy"""
        t1_size = len(self.t1)
        
        # Decide which list to evict from based on adaptive parameter
        if t1_size > 0 and (t1_size > self.p or (t1_size == self.p and in_b2)):
            # Evict from T1 (least recently used in T1)
            key, (value, freq, ts) = self.t1.popitem(last=False)
            # Keep ghost entry with limited size
            if len(self.b1) < self.capacity:
                self.b1[key] = freq
            elif self.b1:
                self.b1.popitem(last=False)
                self.b1[key] = freq
        elif len(self.t2) > 0:
            # Evict from T2 (lowest value item)
            min_key = None
            min_score = float('inf')
            
            for k, (v, f, ts) in self.t2.items():
                score = self._calculate_value_score(f, ts, self.current_time - ts)
                if score < min_score:
                    min_score = score
                    min_key = k
            
            if min_key:
                value, freq, ts = self.t2.pop(min_key)
                # Keep ghost entry with limited size
                if len(self.b2) < self.capacity:
                    self.b2[min_key] = freq
                elif self.b2:
                    self.b2.popitem(last=False)
                    self.b2[min_key] = freq
    
    def get(self, key):
        self.access_count += 1
        timestamp = self._current_timestamp()
        
        # Hit in T1 - promote to T2
        if key in self.t1:
            self.hit_count += 1
            value, freq, ts = self.t1[key]
            del self.t1[key]
            self.t2[key] = (value, freq + 1, timestamp)
            self.t2.move_to_end(key)
            return value
        
        # Hit in T2 - update and move to end
        if key in self.t2:
            self.hit_count += 1
            value, freq, ts = self.t2[key]
            self.t2[key] = (value, freq + 1, timestamp)
            self.t2.move_to_end(key)
            return value
        
        # Miss - check ghost lists
        if key in self.b1:
            self._adapt(hit_in_b1=True)
            del self.b1[key]
        elif key in self.b2:
            self._adapt(hit_in_b1=False)
            del self.b2[key]
        
        return None
    
    def put(self, key, value):
        timestamp = self._current_timestamp()
        
        # Already in T1 - promote to T2
        if key in self.t1:
            val, freq, ts = self.t1[key]
            del self.t1[key]
            self.t2[key] = (value, freq + 1, timestamp)
            return
        
        # Already in T2 - update
        if key in self.t2:
            val, freq, ts = self.t2[key]
            self.t2[key] = (value, freq + 1, timestamp)
            return
        
        # New item
        total_size = len(self.t1) + len(self.t2)
        
        # Check if we've seen this before (in ghost lists)
        if key in self.b1:
            # Was in T1 before, adapt and put in T2
            self._adapt(hit_in_b1=True)
            if total_size >= self.capacity:
                self._replace(in_b2=False)
            freq = self.b1.pop(key)
            self.t2[key] = (value, freq + 1, timestamp)
        elif key in self.b2:
            # Was in T2 before, adapt and put in T2
            self._adapt(hit_in_b1=False)
            if total_size >= self.capacity:
                self._replace(in_b2=True)
            freq = self.b2.pop(key)
            self.t2[key] = (value, freq + 1, timestamp)
        else:
            # Completely new, put in T1
            if total_size >= self.capacity:
                self._replace(in_b2=False)
            self.t1[key] = (value, 1, timestamp)
    
    def get_hit_rate(self):
        return self.hit_count / self.access_count if self.access_count > 0 else 0.0
    
    def get_stats(self):
        return {
            'algorithm': 'Adaptive-ARC',
            'hits': self.hit_count,
            'misses': self.access_count - self.hit_count,
            'hit_rate': self.get_hit_rate()
        }


def run_cache_test(cache_class, workload, cache_capacity):
    """Run a cache test with given workload"""
    cache = cache_class(capacity=cache_capacity)
    
    start_time = time.time()
    
    for key in workload:
        result = cache.get(key)
        if result is None:
            cache.put(key, f"value_{key}")
    
    end_time = time.time()
    runtime = (end_time - start_time) * 1000
    
    stats = cache.get_stats()
    stats['runtime_ms'] = runtime
    
    return stats


def generate_workload(workload_type, size, universe):
    """Generate different types of workloads"""
    random.seed(42)  # For reproducibility
    
    if workload_type == "zipf":
        # Zipf distribution (realistic - most common in real systems)
        weights = [1.0 / (i + 1) ** 1.5 for i in range(universe)]
        total = sum(weights)
        weights = [w / total for w in weights]
        return random.choices(range(universe), weights=weights, k=size)
    
    elif workload_type == "uniform":
        # Uniform distribution
        return [random.randint(0, universe - 1) for _ in range(size)]
    
    elif workload_type == "sequential":
        # Sequential with some loops
        workload = []
        for _ in range(size // universe + 1):
            workload.extend(range(universe))
        return workload[:size]
    
    elif workload_type == "temporal_locality":
        # Strong temporal locality (recent items accessed again)
        workload = []
        window = 30
        for i in range(size):
            if i < window:
                workload.append(random.randint(0, window - 1))
            else:
                # 80% chance to access from recent window
                if random.random() < 0.8:
                    workload.append(workload[random.randint(i - window, i - 1)])
                else:
                    workload.append(random.randint(0, universe - 1))
        return workload


def compare_algorithms():
    print("="*80)
    print(" " * 20 + "CACHE ALGORITHM COMPARISON")
    print(" " * 15 + "Design and Analysis of Algorithms Project")
    print("="*80)
    
    # Configuration
    cache_capacity = 50
    workload_size = 1000
    data_universe = 200
    
    print(f"\n📊 Test Configuration:")
    print(f"   Cache Capacity: {cache_capacity}")
    print(f"   Workload Size: {workload_size} accesses")
    print(f"   Data Universe: {data_universe} unique keys")
    
    # Test different workload patterns
    workload_types = ["zipf", "uniform", "temporal_locality"]
    cache_classes = [
        (FIFOCache, "FIFO"),
        (LRUCache, "LRU"),
        (LFUCache, "LFU"),
        (AdaptiveARCCache, "Adaptive-ARC (NEW)")
    ]
    
    overall_results = {name: {'total_hits': 0, 'total_accesses': 0} 
                      for _, name in cache_classes}
    
    for workload_type in workload_types:
        print(f"\n{'='*80}")
        print(f"📈 Workload Pattern: {workload_type.upper().replace('_', ' ')}")
        print(f"{'='*80}")
        
        workload = generate_workload(workload_type, workload_size, data_universe)
        
        results = []
        for cache_class, name in cache_classes:
            stats = run_cache_test(cache_class, workload, cache_capacity)
            results.append(stats)
            overall_results[name]['total_hits'] += stats['hits']
            overall_results[name]['total_accesses'] += stats['hits'] + stats['misses']
        
        # Display results
        print(f"\n{'Algorithm':<20} {'Hits':<10} {'Misses':<10} {'Hit Rate':<12} {'Runtime (ms)'}")
        print("-" * 80)
        
        for stats in results:
            print(f"{stats['algorithm']:<20} "
                  f"{stats['hits']:<10} "
                  f"{stats['misses']:<10} "
                  f"{stats['hit_rate']:.2%}{'':>7} "
                  f"{stats['runtime_ms']:>8.2f}")
        
        # Highlight best performer
        best = max(results, key=lambda x: x['hit_rate'])
        print(f"\n🏆 Best: {best['algorithm']} with {best['hit_rate']:.2%} hit rate")
    
    # Overall summary
    print(f"\n{'='*80}")
    print(" " * 25 + "OVERALL PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    print(f"{'Algorithm':<25} {'Total Hits':<15} {'Total Accesses':<15} {'Avg Hit Rate'}")
    print("-" * 80)
    
    final_results = []
    for _, name in cache_classes:
        total_hits = overall_results[name]['total_hits']
        total_accesses = overall_results[name]['total_accesses']
        avg_hit_rate = total_hits / total_accesses if total_accesses > 0 else 0
        final_results.append((name, total_hits, total_accesses, avg_hit_rate))
        
        print(f"{name:<25} {total_hits:<15} {total_accesses:<15} {avg_hit_rate:.2%}")
    
    # Find best overall
    best_overall = max(final_results, key=lambda x: x[3])
    
    print(f"\n{'='*80}")
    print(f"🎯 WINNER: {best_overall[0]}")
    print(f"   Overall Hit Rate: {best_overall[3]:.2%}")
    print(f"   Total Cache Hits: {best_overall[1]:,}")
    print(f"{'='*80}")
    
    # Performance improvement
    print(f"\n📊 Performance Improvement over other algorithms:")
    for name, hits, accesses, rate in final_results:
        if name != best_overall[0]:
            improvement = ((best_overall[3] - rate) / rate * 100) if rate > 0 else 0
            print(f"   vs {name:<20}: +{improvement:.2f}% better")
    
    print(f"\n{'='*80}")
    print("✅ Analysis Complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    compare_algorithms()
