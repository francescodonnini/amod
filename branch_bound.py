import sys
import time
from typing import Tuple, Optional, Callable

import objective
from job import Job
from selection_policies import min_upper_bound
from slice import JobSlice
from srpt import rule


class Node:
    def __init__(self, scheduled: list[JobSlice], unscheduled: set[Job], last_job: Job = None, parent: 'Node' = None):
        self.scheduled = scheduled
        self.unscheduled = unscheduled
        self.schedule = self.create_schedule(self.scheduled, self.unscheduled)
        self.parent = parent
        self.last_job = last_job

    @staticmethod
    def completion_time(schedule: list[JobSlice]):
        if len(schedule) == 0:
            return 0
        last = max(schedule, key=lambda j: j.start + j.amount)
        return last.completion_time()

    def create_schedule(self, scheduled: list[JobSlice], unscheduled: set[Job]) -> list[JobSlice]:
        return list(scheduled) + rule(unscheduled, self.t())

    def create_child(self, j: Job) -> 'Node':
        scheduled = self.scheduled + [JobSlice(j, max(self.t(), j.release_date), j.duration)]
        unscheduled = self.unscheduled.difference({j})
        return Node(scheduled, unscheduled, j, self)

    def create_children(self) -> list['Node']:
        return [self.create_child(j) for j in self.unscheduled]

    def get_schedule(self) -> list[JobSlice]:
        return self.schedule

    def get_unscheduled(self) -> set[Job]:
        return self.unscheduled

    def t(self) -> int:
        return Node.completion_time(self.scheduled)

    def upper_bound(self) -> int:
        return objective.total_completion_time(self.schedule)

    def is_feasible(self) -> bool:
        return all(map(lambda j: j.is_whole(), self.schedule))


def solve(jobs: set[Job],
          select_policy: Callable[[list[Node]], Node] = min_upper_bound,
          warm_start: Tuple[list[JobSlice], int] = ([], sys.maxsize),
          max_time_seconds: int = 15 * 60) -> (list[JobSlice], int):
    max_time_ns: int = max_time_seconds * int(10e9)
    inc: list[JobSlice]
    val: int
    inc, val = warm_start
    best_ub: int = val
    queue = [Node(scheduled=[], unscheduled=jobs)]
    start = t = time.perf_counter_ns()
    while not time_out(t - start, max_time_ns) and len(queue) > 0:
        n = select_policy(queue)
        if n.is_feasible() and n.upper_bound() < val:
            inc = list(n.get_schedule())
            val = n.upper_bound()
        elif n.upper_bound() < best_ub:
            best_ub = n.upper_bound()
        children: list[Node] = n.create_children()
        queue.extend(prune(children, best_ub))
        t = time.perf_counter_ns()
    if time_out(t - start, max_time_ns):
        print("time out")
    return inc, val


def prune(nodes: list[Node], best_ub: int) -> list[Node]:
    nodes = filter(lambda n: n.upper_bound() <= best_ub, nodes)
    return list(filter(lambda n: not is_dominated(n), nodes))


def time_out(elapsed: int, lim: int) -> bool:
    return elapsed >= lim


def is_dominated(node: Node) -> bool:
    j = max(node.parent.get_unscheduled(), key=lambda x: x.release_date)
    return node.last_job.release_date >= max(j.release_date, node.parent.t()) + j.duration
