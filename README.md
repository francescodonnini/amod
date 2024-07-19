Algoritmo di Branch & Bound per risolvere un problema di scheduling 1/rj/sum(Cj)

Esempio per utilizzare l'algoritmo
```python
from benchmark import Info
from branch_bound import solve
from heuristics import aprtf
from job import load_csv
from node_queue import LeastCostQueue
from objective import total_completion_time

jobs = load_csv('path/to/file.csv')
info = Info(set(jobs), 'aprtf')
sol = aprtf(jobs)
val = total_completion_time(sol)
inc, val = solve(set(jobs), lambda x: LeastCostQueue(x), info, (sol, val))
```

I file .csv che contengono i job sono del tipo (ci si aspetta che i nomi dei job siano interi)
```csv
job,release,duration
0,6,15
1,3,22
2,9,7
3,9,88
4,4,62
5,9,50
6,6,94
```

È possibile salvare in .csv lo schedule trovato dall'algoritmo
```python
from slice import save_csv

# ...
save_csv('path/to/file', schedule)
```

Per generare delle istanze di esempio sono forniti due generatori (in generator.py)

```python
from generator import HaririPotts

g = HaririPotts()
# vengono generati 20 job
jobs = g.generate_instances(20)
# ...
```

Per utilizzare il solver di gurobi
```python
from mip import solve

# genera o leggi una sequenza di jobs
jobs = ...
# si consiglia di specificare questo parametro perché per alcune istanza gurobi
# non è in grado, di default, di produrre una soluzione intera
solve(jobs, integrality_focus=1)
```