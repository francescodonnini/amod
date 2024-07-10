from typing import Tuple, Optional

from job import Job
from slice import JobSlice


class Info:
    def __init__(self, instance: set[Job], heuristic: str):
        self.instance = instance
        self.heuristic = heuristic
        self.node_count = 0
        self.time_ns = 0

    def __str__(self):
        s = 'job' + '\t'.join([j.identifier for j in self.instance]) + '\n'
        s += 'rj' + '\t'.join([str(j.release_date) for j in self.instance]) + '\n'
        s += 'pj' + '\t'.join([str(j.duration) for j in self.instance]) + '\n'
        s += f'heuristic={self.heuristic}\n'
        s += f'node_count={self.node_count}\n'
        return s + f'time={self.time_ns / int(10e9)} ms'

    def add_node_count(self, c: int):
        if c < 0:
            raise ValueError('non negative value expected')
        self.node_count += c

    def get_node_count(self) -> int:
        return self.node_count

    def get_time(self) -> int:
        return self.time_ns

    def set_time(self, time_ns: int):
        if time_ns < 0:
            raise ValueError('non negative value expected')
        self.time_ns = time_ns
