import heapq
from abc import ABC, abstractmethod
from collections import deque
from typing import Iterable

from branch_bound import Node


class NodeQueue(ABC):
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def extend(self, items: Iterable[Node]):
        pass

    @abstractmethod
    def pop(self) -> Node:
        pass


class FifoQueue(NodeQueue):
    def __init__(self, items: Iterable[Node]):
        self.items = deque(items)

    def extend(self, items: Iterable[Node]):
        self.items.extend(items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def pop(self) -> Node:
        return self.items.popleft()


class LifoQueue(NodeQueue):
    def __init__(self, items: Iterable[Node]):
        self.items = list(items)

    def extend(self, items: Iterable[Node]):
        self.items.extend(items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def pop(self) -> Node:
        return self.items.pop()


class LeastCostQueue(NodeQueue):
    def __init__(self, items: Iterable[Node]):
        self.items = [(i.value, k, i) for k, i in enumerate(items)]
        self.count = len(self.items)
        heapq.heapify(self.items)

    def extend(self, items: Iterable[Node]):
        for i in items:
            heapq.heappush(self.items, (i.value, self.count, i))
            self.count += 1

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def pop(self) -> Node:
        return heapq.heappop(self.items)[2]
