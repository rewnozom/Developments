# managers/memory.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys
import gc

@dataclass
class MemoryStats:
    """Statistics about memory usage."""
    total_allocated: int
    available: int
    peak_usage: int
    current_usage: int
    timestamp: datetime

class MemoryManager:
    """Manages memory allocation and optimization."""

    def __init__(self, max_memory: int = None):
        self.max_memory = max_memory or self._get_system_memory()
        self.allocated_memory: Dict[str, int] = {}
        self.peak_usage = 0
        self.stats_history: List[MemoryStats] = []

    def allocate(self, key: str, size: int) -> bool:
        """Attempt to allocate memory for a specific purpose."""
        if self.available_memory < size:
            if not self._optimize_memory(size):
                return False
        
        self.allocated_memory[key] = size
        current_usage = self.current_usage
        if current_usage > self.peak_usage:
            self.peak_usage = current_usage
            
        self._record_stats()
        return True

    def deallocate(self, key: str) -> bool:
        """Deallocate memory for a specific purpose."""
        if key in self.allocated_memory:
            del self.allocated_memory[key]
            self._record_stats()
            return True
        return False

    def check_availability(self, size: int) -> bool:
        """Check if requested memory is available."""
        return self.available_memory >= size

    def optimize(self) -> int:
        """Optimize memory usage and return freed memory."""
        return self._optimize_memory(0)

    @property
    def current_usage(self) -> int:
        """Get current memory usage."""
        return sum(self.allocated_memory.values())

    @property
    def available_memory(self) -> int:
        """Get available memory."""
        return self.max_memory - self.current_usage

    def get_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        stats = MemoryStats(
            total_allocated=self.max_memory,
            available=self.available_memory,
            peak_usage=self.peak_usage,
            current_usage=self.current_usage,
            timestamp=datetime.now()
        )
        self.stats_history.append(stats)
        return stats

    def get_allocation_by_key(self, key: str) -> Optional[int]:
        """Get memory allocation for specific key."""
        return self.allocated_memory.get(key)

    def _optimize_memory(self, required_size: int) -> bool:
        """Optimize memory usage to free up required size."""
        if self.available_memory >= required_size:
            return True

        # Trigger garbage collection
        gc.collect()

        # Calculate still needed memory
        needed = required_size - self.available_memory
        if needed <= 0:
            return True

        # Try to free low-priority allocations
        freed = self._free_low_priority_allocations(needed)
        if freed >= needed:
            return True

        return False

    def _free_low_priority_allocations(self, needed: int) -> int:
        """Free low-priority memory allocations."""
        freed = 0
        low_priority_keys = self._identify_low_priority_keys()
        
        for key in low_priority_keys:
            if freed >= needed:
                break
            size = self.allocated_memory[key]
            if self.deallocate(key):
                freed += size

        return freed

    def _identify_low_priority_keys(self) -> List[str]:
        """Identify low-priority memory allocations."""
        # Implement priority-based identification
        return sorted(
            self.allocated_memory.keys(),
            key=lambda k: self.allocated_memory[k]
        )

    def _get_system_memory(self) -> int:
        """Get system memory limit."""
        try:
            import psutil
            return psutil.virtual_memory().total
        except ImportError:
            return sys.maxsize

    def _record_stats(self) -> None:
        """Record current memory statistics."""
        self.get_stats()

    def get_stats_history(self) -> List[MemoryStats]:
        """Get memory statistics history."""
        return self.stats_history

    def clear_stats_history(self) -> None:
        """Clear memory statistics history."""
        self.stats_history.clear()

class MemoryError(Exception):
    """Base class for memory-related errors."""
    pass

class MemoryAllocationError(MemoryError):
    """Raised when memory allocation fails."""
    def __init__(self, message: str, required: int, available: int):
        super().__init__(message)
        self.required = required
        self.available = available

class MemoryOptimizationError(MemoryError):
    """Raised when memory optimization fails."""
    pass