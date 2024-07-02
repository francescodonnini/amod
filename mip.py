import gurobipy as gp

from job import Job


def solve(jobs: list[Job]) -> gp.Model:
    indexes: list[int] = list(range(len(jobs)))
    releases: list[int] = [jobs[i].release_date for i in indexes]
    durations: list[int] = [jobs[i].duration for i in indexes]
    m: gp.Model = gp.Model()
    x = m.addVars(indexes, indexes, vtype=gp.GRB.BINARY, name='x')
    c = m.addVars(indexes, vtype=gp.GRB.INTEGER, lb=0, ub=gp.GRB.INFINITY, obj=1, name='c')
    for i in indexes:
        m.addConstr(lhs=gp.quicksum(x[i, j] for j in indexes), sense=gp.GRB.EQUAL, rhs=1, name=f'r[1,{i}]')
    for j in indexes:
        m.addConstr(lhs=gp.quicksum(x[i, j] for i in indexes), sense=gp.GRB.EQUAL, rhs=1, name=f'r[2, {j}]')
    for j in indexes:
        m.addConstr(lhs=c[j], sense=gp.GRB.GREATER_EQUAL, rhs=gp.quicksum((releases[i]+durations[i])*x[i, j] for i in indexes), name=f'r[3,{j}]')
    for j in indexes[1:]:
        m.addConstr(lhs=c[j], sense=gp.GRB.GREATER_EQUAL, rhs=c[j-1] + gp.quicksum(durations[i]*x[i, j] for i in indexes), name=f'r[4,{j}]')
    m.setObjective(gp.quicksum(c[j] for j in indexes), gp.GRB.MINIMIZE)
    m.optimize()
    print_solution(m, x, c, jobs)
    return m


def print_solution(model: gp.Model, x, c, jobs: list[Job]):
    print(f'Solution cost = {model.objVal}')
    for i in range(len(jobs)):
        for j in range(len(jobs)):
            print(x[i, j], sep=',')
        print()
    for i in range(len(jobs)):
        print(f'C[{i}]={c[i]}')
