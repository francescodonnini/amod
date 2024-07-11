import sys
from typing import Callable, Iterable

from job import Job
from slice import JobSlice


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
    return min(sorted(jobs, key=lambda j: ci(j, t)), key=lambda j: ri(j, t))


def est_rule(jobs: Iterable[Job], t: int) -> Job:
    return min(sorted(jobs, key=lambda j: ri(j, t)), key=lambda j: j.duration)


def prtf_rule(jobs: Iterable[Job], t: int) -> Job:
    return min(sorted(jobs, key=lambda j: prio_rule(j, t)), key=lambda j: ri(j, t))


def prio_rule(x: Job, t: int) -> int:
    return 2 * max(t, x.release_date) + x.duration


def ri(j: Job, t: int) -> int:
    return max(j.release_date, t)


def ci(j: Job, t: int) -> int:
    return max(j.release_date, t) + j.duration
