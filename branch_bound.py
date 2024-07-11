import sys
import time
from collections import defaultdict
from typing import Tuple, Callable

import objective
from benchmark import Info
from job import Job
from slice import JobSlice
from srpt import rule


class Node:
    def __init__(self, scheduled: list[JobSlice], unscheduled: set[Job], last_job: Job = None, parent: 'Node' = None):
        self.scheduled = scheduled
        self._t = Node.completion_time(scheduled)
        self.unscheduled = unscheduled
        self.schedule = self.create_schedule(self.scheduled, self.unscheduled)
        self._upper_bound = objective.total_completion_time(self.schedule)
        self.parent = parent
        self.last_job = last_job

    @staticmethod
    def completion_time(schedule: list[JobSlice]):
        if len(schedule) == 0:
            return 0
        last = max(schedule, key=lambda j: j.start + j.amount)
        return last.completion_time()

    def create_schedule(self, scheduled: list[JobSlice], unscheduled: set[Job]) -> list[JobSlice]:
        if len(unscheduled) == 0:
            return list(scheduled)
        schedule: list[JobSlice] = rule(unscheduled, self.t())
        return list(scheduled) + schedule

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
        return self._t

    def upper_bound(self) -> int:
        return self._upper_bound

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
        if n.is_feasible() and n.upper_bound() < val:
            inc = list(n.get_schedule())
            val = n.upper_bound()
        if not n.is_leaf():
            children: list[Node] = n.create_children()
            children = prune(children, val)
            benchmark.add_node_count(len(children))
            queue.extend(children)
        t = time.perf_counter_ns()
    benchmark.set_time(t - start)
    return inc, val


def prune(nodes: list[Node], best_ub: int) -> list[Node]:
    f = filter(lambda n: n.upper_bound() <= best_ub, nodes)
    f = filter(lambda n: not is_dominated(n), f)
    nodes = list(f)
    if len(nodes) <= 1:
        return nodes
    parent = nodes[0].parent
    t = parent.t()
    n = len(parent.unscheduled)
    dominated = defaultdict(lambda: False)
    for n_i in nodes:
        if rule1(n_i, parent.scheduled, n):
            dominated[n_i] = True
            continue
        others = filter(lambda x: x != n_i and x not in dominated, nodes)
        if any(filter(lambda n_j: rule2(n_i, n_j, t, n - 1), others)):
            dominated[n_i] = True
            continue
        if any(filter(lambda n_j: rule3(n_i, n_j, t, n), others)):
            dominated[n_i] = True
    return list(filter(lambda x: x not in dominated, nodes))


def is_dominated(node: Node) -> bool:
    j = max(node.parent.get_unscheduled(), key=lambda x: x.release_date)
    return node.last_job.release_date >= max(j.release_date, node.parent.t()) + j.duration


# Thm. 9 (vedi Chu[1992]).
def rule1(n_i: Node, fixed: list[JobSlice], card: int) -> bool:
    i = n_i.last_job
    for k in range(len(fixed)):
        j = fixed[k]
        tj = delta_j(fixed, k)
        if ei(i, tj) <= ei(j.job, tj) and ei(i, tj) - ei(j.job, tj) <= (i.duration - j.amount) * card:
            return True
    return False


# Thm. 6 (vedi Chu[1992])
def rule2(m: Node, n: Node, t: int, card: int) -> bool:
    i, j = m.last_job, n.last_job
    e1 = ei(i, t)
    e2 = ei(j, t)
    return e1 >= e2 and e1 - e2 >= (i.duration - j.duration) * card


# Thm. 7 (vedi Chu[1992]).
def rule3(m: Node, n: Node, t: int, card: int) -> bool:
    i = m.last_job
    j = n.last_job
    e1 = ei(i, t)
    e2 = ei(j, t)
    return e1 <= e2 and i.duration - j.duration <= (e1 - e2) * card


def delta_j(schedule: list[JobSlice], j: int) -> int:
    if j == 0:
        return -sys.maxsize
    else:
        return schedule[j - 1].completion_time()


def ri(i: Job, t: int) -> int:
    return max(i.release_date, t)


def ei(i: Job, t: int) -> int:
    return ri(i, t) + i.duration


def time_out(elapsed: int, lim: int) -> bool:
    return elapsed >= lim
