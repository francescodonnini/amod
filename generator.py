import random
from abc import ABC, abstractmethod

from job import Job


class RandomIntegerGenerator(ABC):
    @abstractmethod
    def get_next(self) -> int:
        pass


class Normal(RandomIntegerGenerator):
    def __init__(self, mu: int, sigma: float):
        self.mu = mu
        self.sigma = sigma

    def get_next(self) -> int:
        return int(random.normalvariate(self.mu, self.sigma))


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
        jobs.append(Job(str(i), non_negative(release_generator), positive(duration_generator)))
    return jobs


def non_negative(generator: RandomIntegerGenerator) -> int:
    n = generator.get_next()
    while n < 0:
        n = generator.get_next()
    return n


def positive(generator: RandomIntegerGenerator) -> int:
    n = generator.get_next()
    while n <= 0:
        n = generator.get_next()
    return n
