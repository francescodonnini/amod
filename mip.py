import math
from typing import Tuple, Union

import gurobipy as gp
from gurobipy import tupledict, Var

from job import Job
from slice import JobSlice


def solve(jobs: list[Job], verbose: bool = False) -> Union[Tuple[list[JobSlice], int], None]:
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', verbose)
        env.start()
        with gp.Model(env=env) as m:
            indexes: list[int] = list(range(len(jobs)))
            releases: list[int] = [jobs[i].release_date for i in indexes]
            durations: list[int] = [jobs[i].duration for i in indexes]
            x = m.addVars(indexes, indexes, vtype=gp.GRB.BINARY, name='x')
            c = m.addVars(indexes, vtype=gp.GRB.INTEGER, lb=0, ub=gp.GRB.INFINITY, obj=1, name='c')
            for i in indexes:
                m.addConstr(lhs=gp.quicksum(x[i, j] for j in indexes), sense=gp.GRB.EQUAL, rhs=1)
            for j in indexes:
                m.addConstr(lhs=gp.quicksum(x[i, j] for i in indexes), sense=gp.GRB.EQUAL, rhs=1)
            for j in indexes:
                m.addConstr(lhs=c[j], sense=gp.GRB.GREATER_EQUAL, rhs=gp.quicksum((releases[i]+durations[i])*x[i, j] for i in indexes))
            for j in indexes[1:]:
                m.addConstr(lhs=c[j], sense=gp.GRB.GREATER_EQUAL, rhs=c[j-1] + gp.quicksum(durations[i]*x[i, j] for i in indexes))
            m.setObjective(gp.quicksum(c[j] for j in indexes), gp.GRB.MINIMIZE)
            m.optimize()
            return create_schedule(x, c, jobs), int(m.objVal)


def create_schedule(x: tupledict[int, Var], c: tupledict[int, Var], jobs: list[Job]) -> list[JobSlice]:
    schedule = [0] * len(jobs)
    for i in range(len(jobs)):
        for j in range(len(jobs)):
            x_ij = x[i, j].X
            if math.isclose(x_ij, 1.0):
                c_j = c[j].X
                schedule[j] = JobSlice(jobs[i], c_j, jobs[i].duration)
    return schedule


def print_solution(model: gp.Model, x, c, jobs: list[Job]):
    print(f'Solution cost = {model.objVal}')
    schedule: list[int] = []
    for i in range(len(jobs)):
        for j in range(len(jobs)):
            if not math.isclose(x[i, j].X, 0.0):
                schedule.append(j + 1)
    print(', '.join([str(x) for x in schedule]))
    print(', '.join(str(c[i].X) for i in range(len(jobs))))
