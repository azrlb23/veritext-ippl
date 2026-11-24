from __future__ import annotations

from collections import OrderedDict
import time
from typing import Generic, TypeVar

T = TypeVar("T")


class BoundedTTLCache(Generic[T]):
    """Cache in-memory berkapasitas terbatas (LRU) dengan kedaluwarsa TTL."""

    def __init__(self, max_size: int = 2048, ttl_s: int = 3600) -> None:
        self.max_size = max_size
        self.ttl_s = ttl_s
        self._data: OrderedDict[str, tuple[T, float]] = OrderedDict()

    def clear(self) -> None:
        self._data.clear()

    def get(self, key: str) -> tuple[bool, T | None]:
        entry = self._data.get(key)
        if entry is None:
            return False, None
        val, expires_at = entry
        if expires_at <= time.time():
            self._data.pop(key, None)
            return False, None
        self._data.move_to_end(key)
        return True, val

    def set(self, key: str, value: T) -> None:
        self._data[key] = (value, time.time() + self.ttl_s)
        self._data.move_to_end(key)
        while len(self._data) > self.max_size:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        hit, _ = self.get(key)
        return hit
