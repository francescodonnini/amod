import sys
import time
from functools import cached_property
from typing import Tuple, Callable, Optional

import objective
from benchmark import Info
from job import Job
from slice import JobSlice
from srpt import rule


class Node:
    def __init__(self, scheduled: list[JobSlice], unscheduled: set[Job], parent: 'Node' = None):
        self.scheduled = scheduled
        self.unscheduled = unscheduled
        self.schedule = self.create_schedule(self.scheduled, self.unscheduled)
        self.parent = parent

    def create_schedule(self, scheduled: list[JobSlice], unscheduled: set[Job]) -> list[JobSlice]:
        if len(unscheduled) == 0:
            return list(scheduled)
        schedule: list[JobSlice] = rule(unscheduled, self.t)
        return list(scheduled) + schedule

    def create_child(self, j: Job) -> 'Node':
        scheduled: list[JobSlice] = self.scheduled + [JobSlice(j, max(self.t, j.release_date), j.duration)]
        unscheduled: set[Job] = self.unscheduled.difference({j})
        return Node(scheduled, unscheduled, self)

    def create_children(self) -> list['Node']:
        return [self.create_child(j) for j in self.unscheduled]

    def get_last_job(self) -> Optional[Job]:
        if len(self.scheduled) == 0:
            return None
        else:
            return self.scheduled[-1].job

    def get_parent(self) -> Optional['Node']:
        return self.parent

    def get_schedule(self) -> list[JobSlice]:
        return self.schedule

    def get_scheduled(self) -> list[JobSlice]:
        return self.scheduled

    def get_unscheduled(self) -> set[Job]:
        return self.unscheduled

    @cached_property
    def t(self) -> int:
        return Node.completion_time(self.scheduled)

    @staticmethod
    def completion_time(schedule: list[JobSlice]):
        if len(schedule) == 0:
            return 0
        return schedule[-1].completion_time()

    @cached_property
    def value(self) -> int:
        return objective.total_completion_time(self.schedule)

    def is_feasible(self) -> bool:
        return all(map(lambda j: j.is_whole(), self.schedule))

    def is_leaf(self) -> bool:
        return len(self.unscheduled) == 0


def solve(jobs: set[Job],
          select_policy: Callable[[list[Node]], Node],
          benchmark: Info,
          warm_start: Tuple[list[JobSlice], int] = ([], sys.maxsize),
          max_time_seconds: int = 15 * 60) -> Tuple[list[JobSlice], int]:
    max_time_ns: int = max_time_seconds * int(10e9)
    inc: list[JobSlice]
    val: int
    inc, val = warm_start
    queue = [Node(scheduled=[], unscheduled=jobs)]
    start = t = time.perf_counter_ns()
    while not time_out(t - start, max_time_ns) and len(queue) > 0:
        n = select_policy(queue)
        if n.is_feasible() and n.value < val:
            inc = list(n.get_schedule())
            val = n.value
        if not n.is_leaf():
            children: list[Node] = n.create_children()
            children = prune(children, val)
            benchmark.add_node_count(len(children))
            queue.extend(children)
        t = time.perf_counter_ns()
    benchmark.set_time(t - start)
    return inc, val


def prune(nodes: list[Node], best_ub: int) -> list[Node]:
    f = filter(lambda x: x.value <= best_ub, nodes)
    f = filter(lambda x: not is_dominated(x), f)
    nodes = list(f)
    if len(nodes) <= 1:
        return nodes
    parent: Node = nodes[0].get_parent()
    t: int = parent.t
    n: int = len(parent.get_unscheduled())
    dominated: set[Node] = set()
    for n_i in nodes:
        others = filter(lambda x: x != n_i and x not in dominated, nodes)
        if any(filter(lambda n_j: thm6(n_i, n_j, t, n - 1), others)):
            dominated.add(n_i)
        elif any(filter(lambda n_j: thm7(n_i, n_j, t, n), others)):
            dominated.add(n_i)
    return [x for x in nodes if x not in dominated]


def is_dominated(node: Node) -> bool:
    j: Job = max(node.get_parent().get_unscheduled(), key=lambda x: x.release_date)
    return node.get_last_job().release_date >= max(j.release_date, node.get_parent().t) + j.duration


# Thm. 6 (vedi Chu[1992])
def thm6(m: Node, n: Node, t: int, card: int) -> bool:
    i: Job = m.get_last_job()
    j: Job = n.get_last_job()
    e_i: int = e(i, t)
    e_j: int = e(j, t)
    return e_i >= e_j and e_i - e_j >= (i.duration - j.duration) * card


# Thm. 7 (vedi Chu[1992]).
def thm7(m: Node, n: Node, t: int, card: int) -> bool:
    i: Job = m.get_last_job()
    j: Job = n.get_last_job()
    e_i: int = e(i, t)
    e_j: int = e(j, t)
    return e_i <= e_j and i.duration - j.duration <= (e_i - e_j) * card


# Thm. 9 (vedi Chu[1992]).
def thm9(n_i: Node) -> bool:
    parent: Node = n_i.get_parent()
    i: Job = n_i.get_last_job()
    p_i: int = i.duration
    n: int = len(parent.get_unscheduled())
    scheduled: list[JobSlice] = parent.get_scheduled()
    for k in range(len(scheduled)):
        j: Job = scheduled[k].job
        if j != i:
            p_j: int = j.duration
            d_j: int = delta(scheduled, k)
            e_i: int = e(i, d_j)
            e_j: int = e(j, d_j)
            if e_i <= e_j and e_i - e_j <= (p_i - p_j) * n:
                return True
    return False


# Thm. 10 (vedi Chu[1992])
def thm10(n_i: Node) -> bool:
    parent: Node = n_i.get_parent()
    i: Job = n_i.get_last_job()
    p_i: int = i.duration
    scheduled: list[JobSlice] = parent.get_scheduled()
    for k in range(len(scheduled)):
        j: Job = scheduled[k].job
        p_j: int = j.duration
        d_j: int = delta(scheduled, k)
        e_i: int = e(i, d_j)
        e_j: int = e(j, d_j)
        if p_i >= p_j and p_i - p_j >= (e_i - e_j) * (len(scheduled) - k + 2):
            return True
    return False


def delta(schedule: list[JobSlice], j: int) -> int:
    if j == 0:
        return -sys.maxsize
    else:
        return schedule[j - 1].completion_time()


def r(i: Job, t: int) -> int:
    return max(i.release_date, t)


def e(i: Job, t: int) -> int:
    return r(i, t) + i.duration


def time_out(elapsed: int, lim: int) -> bool:
    return elapsed >= lim
