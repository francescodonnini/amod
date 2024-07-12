import random
from abc import ABC, abstractmethod
from typing import Tuple

from job import Job


class Generator(ABC):
    @abstractmethod
    def generate_instances(self, n: int) -> list[Job]:
        pass


class Dummy(Generator):
    def __init__(self, duration: Tuple[int, int], release: Tuple[int, int], seed: int = 42):
        self.random_stream = random.Random(seed)
        self.duration = duration
        self.releases = release

    def generate_instances(self, n: int) -> list[Job]:
        instances: list[Job] = []
        for i in range(n):
            a, b = self.duration
            pi = self.uniform(a, b)
            a, b = self.releases
            ri = self.uniform(a, b)
            instances.append(Job(str(i), ri, pi))
        return instances

    def uniform(self, a: int, b: int) -> int:
        return uniform(self.random_stream, a, b)


class HaririPotts(Generator):
    def __init__(self, seed: int = 42):
        self.random_stream = random.Random(seed)

    def generate_instances(self, n: int) -> list[Job]:
        duration: Tuple[int, int] = (1, 100)
        r: list[float] = [0.2, 0.4, 0.8, 1.0, 1.25, 1.5, 1.75, 2, 3]
        releases: list[Tuple[int, int]] = [(0, int(5 * n * x)) for x in r]
        instances: list[Job] = []
        for i in range(n):
            a, b = duration
            pi = self.uniform(a, b)
            a, b = releases[i % len(r)]
            ri = self.uniform(a, b)
            instances.append(Job(str(i), ri, pi))
        return instances

    def uniform(self, a: int, b: int) -> int:
        return uniform(self.random_stream, a, b)


def uniform(random_stream: random.Random, a: int, b: int) -> int:
    return int(a + (b - a) * random_stream.random())
