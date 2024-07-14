import sys
import time
from typing import Tuple, Callable, Iterable

from benchmark import Info
from job import Job
from node import Node
from node_queue import NodeQueue
from slice import JobSlice
from timeout import Timeout


def solve(jobs: set[Job],
          queue_factory: Callable[[Iterable[Node]], NodeQueue],
          benchmark: Info,
          warm_start: Tuple[list[JobSlice], int] = ([], sys.maxsize),
          max_time_seconds: int = 15 * 60) -> Tuple[list[JobSlice], int]:
    max_time_ns: int = max_time_seconds * int(1e9)
    inc: list[JobSlice]
    val: int
    inc, val = warm_start
    start = t = time.time_ns()
    root = Node(scheduled=[], unscheduled=jobs)
    benchmark.add_node_count(1)
    if root.is_feasible():
        benchmark.set_time(time.time_ns() - start)
        return list(root.schedule), root.value
    queue = queue_factory([root])
    while not time_out(t - start, max_time_ns) and not queue.is_empty():
        n = queue.pop()
        if n.is_feasible() and n.value < val:
            inc = list(n.get_schedule())
            val = n.value
        if not n.is_leaf():
            children: list[Node] = n.create_children()
            children = prune(children, val)
            benchmark.add_node_count(len(children))
            queue.extend(children)
        t = time.time_ns()
    elapsed = t - start
    benchmark.set_time(elapsed)
    if time_out(elapsed, max_time_ns):
        raise Timeout(inc, val, elapsed)
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
