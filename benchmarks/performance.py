"""
AIUCE Performance Benchmarks
性能基准测试套件

测试范围：
1. 消息总线吞吐量
2. 层级处理延迟
3. 记忆系统查询性能
4. 决策审计写入性能
5. 端到端查询延迟
"""

import time
import asyncio
import statistics
from dataclasses import dataclass
from typing import List, Dict, Any, Callable
from functools import wraps


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    p50_ms: float
    p99_ms: float
    throughput_per_sec: float
    
    def __str__(self) -> str:
        return (
            f"\n{'═' * 50}\n"
            f"  {self.name}\n"
            f"{'═' * 50}\n"
            f"  Iterations: {self.iterations}\n"
            f"  Total Time: {self.total_time_ms:.2f} ms\n"
            f"  Avg: {self.avg_time_ms:.3f} ms\n"
            f"  Min: {self.min_time_ms:.3f} ms\n"
            f"  Max: {self.max_time_ms:.3f} ms\n"
            f"  P50: {self.p50_ms:.3f} ms\n"
            f"  P99: {self.p99_ms:.3f} ms\n"
            f"  Throughput: {self.throughput_per_sec:.1f} ops/s\n"
            f"{'═' * 50}\n"
        )


def benchmark(
    name: str,
    iterations: int = 1000,
    warmup: int = 10
) -> Callable:
    """
    基准测试装饰器
    
    Args:
        name: 测试名称
        iterations: 迭代次数
        warmup: 预热次数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> BenchmarkResult:
            # 预热
            for _ in range(warmup):
                func(*args, **kwargs)
            
            # 正式测试
            times = []
            start_total = time.perf_counter()
            
            for _ in range(iterations):
                start = time.perf_counter()
                func(*args, **kwargs)
                end = time.perf_counter()
                times.append((end - start) * 1000)  # ms
            
            end_total = time.perf_counter()
            total_time = (end_total - start_total) * 1000
            
            # 计算统计
            times_sorted = sorted(times)
            p50_idx = int(len(times_sorted) * 0.5)
            p99_idx = int(len(times_sorted) * 0.99)
            
            return BenchmarkResult(
                name=name,
                iterations=iterations,
                total_time_ms=total_time,
                avg_time_ms=statistics.mean(times),
                min_time_ms=min(times),
                max_time_ms=max(times),
                p50_ms=times_sorted[p50_idx],
                p99_ms=times_sorted[p99_idx],
                throughput_per_sec=iterations / (total_time / 1000),
            )
        
        return wrapper
    return decorator


def async_benchmark(
    name: str,
    iterations: int = 1000,
    warmup: int = 10
) -> Callable:
    """
    异步基准测试装饰器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> BenchmarkResult:
            # 预热
            for _ in range(warmup):
                await func(*args, **kwargs)
            
            # 正式测试
            times = []
            start_total = time.perf_counter()
            
            for _ in range(iterations):
                start = time.perf_counter()
                await func(*args, **kwargs)
                end = time.perf_counter()
                times.append((end - start) * 1000)
            
            end_total = time.perf_counter()
            total_time = (end_total - start_total) * 1000
            
            times_sorted = sorted(times)
            p50_idx = int(len(times_sorted) * 0.5)
            p99_idx = int(len(times_sorted) * 0.99)
            
            return BenchmarkResult(
                name=name,
                iterations=iterations,
                total_time_ms=total_time,
                avg_time_ms=statistics.mean(times),
                min_time_ms=min(times),
                max_time_ms=max(times),
                p50_ms=times_sorted[p50_idx],
                p99_ms=times_sorted[p99_idx],
                throughput_per_sec=iterations / (total_time / 1000),
            )
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# 测试套件
# ═══════════════════════════════════════════════════════════════

class BenchmarkSuite:
    """基准测试套件"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def add_result(self, result: BenchmarkResult):
        """添加测试结果"""
        self.results.append(result)
    
    def run_all(self):
        """运行所有测试"""
        print("\n" + "═" * 60)
        print("  AIUCE Performance Benchmark Suite")
        print("  十一层架构性能基准测试")
        print("═" * 60 + "\n")
        
        # 1. 消息总线测试
        self._benchmark_message_bus()
        
        # 2. 异步消息总线测试
        self._benchmark_async_message_bus()
        
        # 3. 消息创建测试
        self._benchmark_message_creation()
        
        # 4. 层级枚举测试
        self._benchmark_layer_enum()
        
        # 打印摘要
        self._print_summary()
    
    def _benchmark_message_bus(self):
        """消息总线吞吐量测试"""
        from core.message import MessageBus, Message
        
        bus = MessageBus()
        
        # 注册订阅者
        received = []
        
        def callback(msg: Message):
            received.append(msg)
        
        for layer in ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10"]:
            bus.subscribe(layer, callback)
        
        @benchmark("MessageBus.publish()", iterations=10000)
        def test_publish():
            msg = Message(
                source_layer="L0",
                target_layer="L5",
                type="test",
                payload={"data": "benchmark"}
            )
            bus.publish(msg)
        
        result = test_publish()
        self.results.append(result)
        print(result)
    
    def _benchmark_async_message_bus(self):
        """异步消息总线吞吐量测试"""
        from core.async_message import AsyncMessageBus, Message
        import asyncio
        
        bus = AsyncMessageBus()
        received = []
        
        async def callback(msg: Message):
            received.append(msg)
        
        for layer in ["L1", "L2", "L3", "L4", "L5"]:
            bus.async_subscribe(layer, callback)
        
        @async_benchmark("AsyncMessageBus.async_publish()", iterations=5000)
        async def test_async_publish():
            msg = Message(
                source_layer="L0",
                target_layer="L3",
                type="test",
                payload={"data": "benchmark"}
            )
            await bus.async_publish(msg)
        
        result = asyncio.run(test_async_publish())
        self.results.append(result)
        print(result)
    
    def _benchmark_message_creation(self):
        """消息创建性能测试"""
        from core.message import Message
        
        @benchmark("Message creation", iterations=50000)
        def test_create():
            msg = Message(
                source_layer="L2",
                target_layer="L5",
                type="observe",
                payload={"key": "value", "data": [1, 2, 3]}
            )
            _ = msg.to_dict()
        
        result = test_create()
        self.results.append(result)
        print(result)
    
    def _benchmark_layer_enum(self):
        """层级枚举性能测试"""
        from core.message import LayerLevel
        
        @benchmark("LayerLevel property access", iterations=100000)
        def test_enum():
            layer = LayerLevel.L5
            _ = layer.official
            _ = layer.department
            _ = layer.value
        
        result = test_enum()
        self.results.append(result)
        print(result)
    
    def _print_summary(self):
        """打印测试摘要"""
        print("\n" + "═" * 60)
        print("  Benchmark Summary")
        print("═" * 60)
        print(f"  {'Test Name':<40} {'Avg (ms)':<12} {'Throughput':<15}")
        print("  " + "-" * 67)
        
        for result in self.results:
            print(f"  {result.name:<40} {result.avg_time_ms:<12.3f} {result.throughput_per_sec:<15.1f}")
        
        print("═" * 60 + "\n")


# ═══════════════════════════════════════════════════════════════
# 端到端测试
# ═══════════════════════════════════════════════════════════════

def run_e2e_benchmark(system):
    """
    端到端系统测试
    
    Args:
        system: ElevenLayerSystem 实例
    """
    print("\n" + "═" * 60)
    print("  End-to-End Benchmark")
    print("═" * 60 + "\n")
    
    test_queries = [
        "查询今天的天气",
        "帮我分析一下这个项目的风险",
        "总结最近的日记内容",
        "制定一个学习计划",
    ]
    
    times = []
    
    for query in test_queries:
        start = time.perf_counter()
        result = system.run(query)
        end = time.perf_counter()
        
        elapsed = (end - start) * 1000
        times.append(elapsed)
        
        print(f"  Query: {query[:30]}...")
        print(f"  Time: {elapsed:.2f} ms")
        print(f"  Status: {result.get('status', 'unknown')}")
        print()
    
    print("  " + "-" * 40)
    print(f"  Avg E2E Time: {statistics.mean(times):.2f} ms")
    print(f"  Max E2E Time: {max(times):.2f} ms")
    print("═" * 60 + "\n")


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    suite = BenchmarkSuite()
    suite.run_all()
