from functools import cached_property
from typing import Optional

import objective
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