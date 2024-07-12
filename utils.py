import sys
from typing import Callable, Tuple

import objective
from generator import Generator
from job import Job, save_csv
from slice import JobSlice


def best_heuristic(jobs: list[Job], heuristics: dict[str, Callable[[list[Job]], list[JobSlice]]]) -> Tuple[str, list[JobSlice], int]:
    name = 'None'
    sol = []
    val = sys.maxsize
    for k, h in heuristics.items():
        s: list[JobSlice] = h(jobs)
        v: int = objective.total_completion_time(s)
        if v < val:
            name = k
            sol = s
            val = v
    return name, sol, val


def generate(generator: Generator, num_of_jobs: int, num_of_instances: int) -> list[list[Job]]:
    instances: list[list[Job]] = []
    for k in range(num_of_instances):
        instances.append(generator.generate_instances(num_of_jobs))
    return instances


def save_all(instances: list[list[Job]], dir_path: str):
    for i in range(len(instances)):
        save_csv(instances[i], f'{dir_path}/{i}.csv')


def stringify(schedule: list[JobSlice]) -> str:
    s = 'job\t' + '\t'.join([j.job.identifier if j is not None else 'None' for j in schedule]) + '\n'
    s += 's\t' + '\t'.join([str(j.start) if j is not None else 'ND' for j in schedule]) + '\n'
    s += 'amt\t' + '\t'.join([str(j.amount) if j is not None else 'ND' for j in schedule]) + '\n'
    s += 'whl\t' + '\t'.join([str(1 if j is not None and j.is_whole() else 0) for j in schedule]) + '\n'
    return s
