import math
import time
from typing import Tuple, Union

import gurobipy as gp
from gurobipy import tupledict, Var

from job import Job
from slice import JobSlice
from timeout import Timeout


def solve(jobs: list[Job],
          verbose: bool = False,
          max_time_seconds: int = 15 * 60,
          gap: float = 1e-6,
          integrality_focus: int = 0) -> Tuple[list[JobSlice], float, int]:
    with gp.Env(empty=True) as env:
        env.setParam('MIPGap', gap)
        env.setParam('OutputFlag', verbose)
        env.setParam('TimeLimit', max_time_seconds)
        env.setParam('IntegralityFocus', integrality_focus)
        env.start()
        with gp.Model(env=env) as m:
            indexes: list[int] = list(range(len(jobs)))
            releases: list[int] = [jobs[i].release_date for i in indexes]
            durations: list[int] = [jobs[i].duration for i in indexes]
            x = m.addVars(indexes, indexes, vtype=gp.GRB.BINARY, name='x')
            c = m.addVars(indexes, vtype=gp.GRB.INTEGER, lb=0, ub=gp.GRB.INFINITY, name='c')
            for i in indexes:
                m.addConstr(lhs=gp.quicksum(x[i, j] for j in indexes), sense=gp.GRB.EQUAL, rhs=1)
            for j in indexes:
                m.addConstr(lhs=gp.quicksum(x[i, j] for i in indexes), sense=gp.GRB.EQUAL, rhs=1)
            for j in indexes:
                m.addConstr(lhs=c[j], sense=gp.GRB.GREATER_EQUAL, rhs=gp.quicksum((releases[i]+durations[i])*x[i, j] for i in indexes))
            for j in indexes[1:]:
                m.addConstr(lhs=c[j], sense=gp.GRB.GREATER_EQUAL, rhs=c[j-1] + gp.quicksum(durations[i]*x[i, j] for i in indexes))
            m.setObjective(gp.quicksum(c[j] for j in indexes), gp.GRB.MINIMIZE)
            start = time.time_ns()
            m: gp.Model
            m.optimize()
            inc, val, elapsed = create_schedule(x, c, jobs), m.objVal, time.time_ns() - start
            if m.Status == gp.GRB.TIME_LIMIT:
                raise Timeout(inc, val, elapsed)
            return inc, val, elapsed


def create_schedule(x: tupledict[Tuple[int, int], Var], c: tupledict[int, Var], jobs: list[Job]) -> list[JobSlice]:
    schedule: list[Union[JobSlice, None]] = [None] * len(jobs)
    for i in range(len(jobs)):
        for j in range(len(jobs)):
            x_ij = x[i, j].X
            if math.isclose(x_ij, 1.0):
                c_j = int(c[j].X)
                schedule[j] = JobSlice(jobs[i], c_j, jobs[i].duration)
    return schedule

