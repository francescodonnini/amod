import random
from abc import ABC, abstractmethod

from job import Job


class RandomIntegerGenerator(ABC):
    @abstractmethod
    def get_next(self) -> int:
        pass


class Uniform(RandomIntegerGenerator):
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def get_next(self) -> int:
        return int(self.a + (self.b - self.a) * random.random())


def generate_instances(n: int,
                       release_generator: RandomIntegerGenerator,
                       duration_generator: RandomIntegerGenerator,
                       seed: int = 42) -> list[Job]:
    random.seed(seed)
    jobs: list[Job] = []
    for i in range(n):
        jobs.append(Job(str(i), release_generator.get_next(), duration_generator.get_next()))
    return jobs
