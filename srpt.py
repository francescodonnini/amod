from typing import Iterable

from job import Job
from rpt_job import RptJob
from slice import JobSlice


def rule(jobs: Iterable[Job], start: int = 0) -> list[JobSlice]:
    not_completed: list[RptJob] = list(map(create_rpt_job, jobs))
    schedule: list[JobSlice] = []
    m = min(not_completed, key=lambda j: j.release_date)
    t = max(start, m.release_date)
    while len(not_completed) > 0:
        j = min(released(not_completed, t))
        nr = not_released(not_completed, t)
        if len(nr) == 0:
            amount = j.rpt
            not_completed.remove(j)
        else:
            k = min(nr, key=lambda x: x.release_date)
            c_j = t + j.rpt
            if c_j > k.release_date:
                amount = k.release_date - t
            else:
                amount = j.rpt
                not_completed.remove(j)
        j.work(amount)
        add_join(schedule, JobSlice(j, t, amount))
        if len(not_completed) == 0:
            continue
        m = min(not_completed, key=lambda j: j.release_date)
        t = max(t + amount, m.release_date)
    return schedule


def add_join(schedule: list[JobSlice], j: JobSlice):
    if len(schedule) == 0 or schedule[-1].job != j.job:
        schedule.append(j)
    else:
        i = schedule[-1]
        schedule[-1] = JobSlice(i.job, i.start, i.amount + j.amount)


def create_rpt_job(j: Job) -> RptJob:
    return RptJob(j.identifier, j.release_date, j.duration)


def released(jobs: list[RptJob], t: int) -> list[RptJob]:
    return list(filter(lambda j: j.release_date <= t and j.rpt > 0, jobs))


def not_released(jobs: list[RptJob], t: int) -> list[RptJob]:
    return list(filter(lambda j: j.release_date > t, jobs))
