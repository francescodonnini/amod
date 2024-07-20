import sys
from typing import Callable, Iterable, Any

import objective
from job import Job
from slice import JobSlice


def aprtf(jobs: list[Job]) -> list[JobSlice]:
    unscheduled: set[Job] = set(jobs)
    schedule: list[JobSlice] = []
    t: int = -sys.maxsize
    while len(unscheduled) > 0:
        a: Job = min_prio(unscheduled, t)
        b: Job = min_release(unscheduled, t)
        x: Job
        if a.release_date <= ri(b, t):
            x = a
        else:
            mu: int = len(unscheduled) - 2
            tau: int = smallest_release_date(unscheduled.difference({a, b}))
            if f(a, b, t) - f(b, a, t) < mu * min(ri(a, t) - ri(b, t), ei(b, ei(a, t)) - tau):
                x = b
            else:
                x = a
        schedule.append(JobSlice(x, max(t, x.release_date), x.duration))
        t = ei(x, t)
        unscheduled.remove(x)
    return schedule


def smallest_release_date(jobs: Iterable[Job]) -> int:
    m: Job = min(jobs, key=lambda x: x.release_date, default=None)
    if m is None:
        return 0
    else:
        return m.release_date


def min_prio(jobs: Iterable[Job], t: int) -> Job:
    minimums: list[Job] = abstract_min(jobs, key=lambda x: prio_rule(x, t))
    if len(minimums) == 1:
        return minimums[0]
    minimums = abstract_min(minimums, key=lambda x: ri(x, t))
    if len(minimums) == 1:
        return minimums[0]
    return min(minimums, key=lambda x: int(x.identifier))


def min_release(jobs: Iterable[Job], t: int) -> Job:
    minimums: list[Job] = abstract_min(jobs, key=lambda x: ri(x, t))
    if len(minimums) == 1:
        return minimums[0]
    minimums = abstract_min(minimums, key=lambda x: x.duration)
    if len(minimums) == 1:
        return minimums[0]
    return min(minimums, key=lambda x: int(x.identifier))


def abstract_min(jobs: Iterable[Job], key: Callable[[Job], Any]) -> list[Job]:
    m: Job = min(jobs, key=lambda x: key(x))
    return list(filter(lambda x: key(x) == key(m), jobs))


def prtf(jobs: list[Job]) -> list[JobSlice]:
    return heuristic(jobs, prtf_rule)


def ect(jobs: list[Job]) -> list[JobSlice]:
    return heuristic(jobs, ect_rule)


def est(jobs: list[Job]) -> list[JobSlice]:
    return heuristic(jobs, est_rule)


def heuristic(jobs: list[Job], select_job: Callable[[Iterable[Job], int], Job]) -> list[JobSlice]:
    t: int = -sys.maxsize
    unscheduled_jobs: list[Job] = list(jobs)
    schedule: list[JobSlice] = []
    while len(unscheduled_jobs) > 0:
        x = select_job(unscheduled_jobs, t)
        schedule.append(JobSlice(x, ri(x, t), x.duration))
        unscheduled_jobs.remove(x)
        t = ci(x, t)
    return schedule


def ect_rule(jobs: Iterable[Job], t: int) -> Job:
    ties: list[Job] = abstract_min(jobs, key=lambda j: ci(j, t))
    if len(ties) > 1:
        return min(ties, key=lambda j: ri(j, t))
    return ties[0]


def est_rule(jobs: Iterable[Job], t: int) -> Job:
    ties: list[Job] = abstract_min(jobs, key=lambda j: ri(j, t))
    if len(ties) > 1:
        return min(ties, key=lambda j: j.duration)
    return ties[0]


def prtf_rule(jobs: Iterable[Job], t: int) -> Job:
    ties: list[Job] = abstract_min(jobs, key=lambda j: prio_rule(j, t))
    if len(ties) > 1:
        return min(ties, key=lambda j: ri(j, t))
    return ties[0]


def prio_rule(x: Job, t: int) -> int:
    return 2 * max(t, x.release_date) + x.duration


def ei(j: Job, t: int) -> int:
    return ri(j, t) + j.duration


def ri(j: Job, t: int) -> int:
    return max(j.release_date, t)


def ci(j: Job, t: int) -> int:
    return max(j.release_date, t) + j.duration


def f(a: Job, b: Job, t: int) -> int:
    s1 = JobSlice(a, max(a.release_date, t), a.duration)
    schedule = [s1, JobSlice(b, max(s1.completion_time(), b.release_date), b.duration)]
    return objective.total_completion_time(schedule)
