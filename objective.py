from typing import Iterable

from job import Job
from slice import JobSlice


def total_completion_time(schedule: Iterable[JobSlice]) -> int:
    completions: dict[Job, int] = {}
    for j in schedule:
        completions[j.job] = j.start + j.amount
    return sum(completions.values())
