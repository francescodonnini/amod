from collections import deque
from typing import Iterable, Union

from job import Job
from rpt_job import RptJob
from slice import JobSlice


def rule(jobs: Iterable[Job], start: int = 0) -> list[JobSlice]:
    not_completed: list[RptJob] = list(map(create_rpt_job, jobs))
    schedule: deque[JobSlice] = deque()
    m = min(not_completed, key=lambda x: x.release_date)
    t = max(start, m.release_date)
    while len(not_completed) > 0:
        j = min_released(not_completed, t)
        amount = j.rpt
        if len(not_completed) > 1:
            for i in range(1, j.rpt):
                if use_preemption(not_completed, t + i, j.expected_rpt(i)):
                    amount = i
                    break
        j.work(amount)
        add_join(schedule, JobSlice(j, t, amount))
        if j.is_completed():
            not_completed.remove(j)
        if len(not_completed) == 0:
            break
        m = min(not_completed, key=lambda x: x.release_date)
        t = max(t + amount, m.release_date)
    return list(schedule)


def add_join(schedule: deque[JobSlice], j: JobSlice):
    if len(schedule) == 0 or schedule[-1].job != j.job:
        schedule.append(j)
    else:
        i = schedule[-1]
        schedule[-1] = JobSlice(i.job, i.start, i.amount + j.amount)


def create_rpt_job(j: Job) -> RptJob:
    return RptJob(j.identifier, j.release_date, j.duration)


def min_released(jobs: Iterable[RptJob], t: int) -> RptJob:
    m: Union[RptJob, None] = None
    for j in jobs:
        if j.release_date <= t and (m is None or m.rpt > j.rpt):
            m = j
    return m


def use_preemption(jobs: Iterable[RptJob], t: int, rpt: int) -> bool:
    for j in jobs:
        if j.release_date == t and j.rpt < rpt:
            return True
    return False
