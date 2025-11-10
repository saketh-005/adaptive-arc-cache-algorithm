import time
import random
from collections import OrderedDict


class AdaptiveARCCache:
    
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.t1 = OrderedDict()
        self.t2 = OrderedDict()
        self.b1 = OrderedDict()
        self.b2 = OrderedDict()
        self.p = capacity // 2
        self.access_count = 0
        self.hit_count = 0
        self.current_time = 0
        
    def _current_timestamp(self):
        self.current_time += 1
        return self.current_time
    
    def _calculate_value_score(self, frequency, timestamp, age):
        recency = max(1, self.current_time - timestamp + 1)
        recency_score = 1.0 / (recency ** 0.5)
        frequency_score = frequency ** 1.2
        score = frequency_score * recency_score
        return score
    
    def _adapt(self, hit_in_b1):
        if hit_in_b1:
            delta = max(1, len(self.b2) // max(len(self.b1), 1))
            self.p = min(self.p + delta, self.capacity)
        else:
            delta = max(1, len(self.b1) // max(len(self.b2), 1))
            self.p = max(self.p - delta, 0)
    
    def _replace(self, in_b2):
        t1_size = len(self.t1)
        
        if t1_size > 0 and (t1_size > self.p or (t1_size == self.p and in_b2)):
            key, (value, freq, ts) = self.t1.popitem(last=False)
            if len(self.b1) < self.capacity:
                self.b1[key] = freq
            elif self.b1:
                self.b1.popitem(last=False)
                self.b1[key] = freq
        elif len(self.t2) > 0:
            min_key = None
            min_score = float('inf')
            
            for k, (v, f, ts) in self.t2.items():
                score = self._calculate_value_score(f, ts, self.current_time - ts)
                if score < min_score:
                    min_score = score
                    min_key = k
            
            if min_key:
                value, freq, ts = self.t2.pop(min_key)
                if len(self.b2) < self.capacity:
                    self.b2[min_key] = freq
                elif self.b2:
                    self.b2.popitem(last=False)
                    self.b2[min_key] = freq
    
    def get(self, key):
        self.access_count += 1
        timestamp = self._current_timestamp()
        
        if key in self.t1:
            self.hit_count += 1
            value, freq, ts = self.t1[key]
            del self.t1[key]
            self.t2[key] = (value, freq + 1, timestamp)
            self.t2.move_to_end(key)
            return value
        
        if key in self.t2:
            self.hit_count += 1
            value, freq, ts = self.t2[key]
            self.t2[key] = (value, freq + 1, timestamp)
            self.t2.move_to_end(key)
            return value
        
        if key in self.b1:
            self._adapt(hit_in_b1=True)
            del self.b1[key]
        
        elif key in self.b2:
            self._adapt(hit_in_b1=False)
            del self.b2[key]
        
        return None
    
    def put(self, key, value):
        timestamp = self._current_timestamp()
        
        if key in self.t1:
            val, freq, ts = self.t1[key]
            del self.t1[key]
            self.t2[key] = (value, freq + 1, timestamp)
            return
        
        if key in self.t2:
            val, freq, ts = self.t2[key]
            self.t2[key] = (value, freq + 1, timestamp)
            return
        
        total_size = len(self.t1) + len(self.t2)
        
        if key in self.b1:
            self._adapt(hit_in_b1=True)
            if total_size >= self.capacity:
                self._replace(in_b2=False)
            freq = self.b1.pop(key)
            self.t2[key] = (value, freq + 1, timestamp)
        elif key in self.b2:
            self._adapt(hit_in_b2=False)
            if total_size >= self.capacity:
                self._replace(in_b2=True)
            freq = self.b2.pop(key)
            self.t2[key] = (value, freq + 1, timestamp)
        else:
            if total_size >= self.capacity:
                self._replace(in_b2=False)
            self.t1[key] = (value, 1, timestamp)
    
    def get_hit_rate(self):
        if self.access_count == 0:
            return 0.0
        return self.hit_count / self.access_count
    
    def get_stats(self):
        return {
            'algorithm': 'Adaptive-ARC',
            'capacity': self.capacity,
            'size': len(self.t1) + len(self.t2),
            't1_size': len(self.t1),
            't2_size': len(self.t2),
            'b1_size': len(self.b1),
            'b2_size': len(self.b2),
            'adaptive_p': self.p,
            'accesses': self.access_count,
            'hits': self.hit_count,
            'misses': self.access_count - self.hit_count,
            'hit_rate': self.get_hit_rate()
        }
    
    def clear(self):
        self.t1.clear()
        self.t2.clear()
        self.b1.clear()
        self.b2.clear()
        self.p = self.capacity // 2
        self.access_count = 0
        self.hit_count = 0
        self.current_time = 0


def demo_adaptive_arc():
    print("="*70)
    print("Adaptive ARC (Adaptive Replacement Cache) Demonstration")
    print("Novel Hybrid Algorithm combining Recency + Frequency + Adaptation")
    print("="*70)
    
    cache_capacity = 50
    cycles = 40
    hot_size = 20
    hot_accesses = 50
    burst_size = 50

    print(f"\nConfiguration:")
    print(f"  Cache Capacity: {cache_capacity}")
    print(f"  Workload: cycles={cycles}, hot_size={hot_size}, hot_accesses={hot_accesses}, burst_size={burst_size}")

    cache = AdaptiveARCCache(capacity=cache_capacity)

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
    
    print("Running test with adaptive learning...")
    start_time = time.time()
    
    for key in workload:
        result = cache.get(key)
        if result is None:
            cache.put(key, f"value_{key}")
    
    end_time = time.time()
    runtime = (end_time - start_time) * 1000
    
    stats = cache.get_stats()
    
    print("\n" + "="*70)
    print("RESULTS - ADAPTIVE ARC CACHE")
    print("="*70)
    print(f"Algorithm:        {stats['algorithm']}")
    print(f"Cache Size:       {stats['size']}/{stats['capacity']}")
    print(f"  ├─ T1 (Recent): {stats['t1_size']}")
    print(f"  └─ T2 (Frequent): {stats['t2_size']}")
    print(f"Ghost Lists:      B1={stats['b1_size']}, B2={stats['b2_size']}")
    print(f"Adaptive Param:   p = {stats['adaptive_p']}")
    print(f"\nTotal Accesses:   {stats['accesses']}")
    print(f"Cache Hits:       {stats['hits']}")
    print(f"Cache Misses:     {stats['misses']}")
    print(f"Hit Rate:         {stats['hit_rate']:.2%}")
    print(f"Runtime:          {runtime:.2f} ms")
    print(f"Avg per access:   {runtime/len(workload):.4f} ms")
    print("="*70)
    
    return stats


if __name__ == "__main__":
    demo_adaptive_arc()
