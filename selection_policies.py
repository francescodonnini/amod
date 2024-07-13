from branch_bound import Node


def best_fit(nodes: list[Node]) -> Node:
    m = min(nodes, key=lambda n: n.value)
    nodes.remove(m)
    return m


def fifo(nodes: list[Node]) -> Node:
    return nodes.pop(0)


def lifo(nodes: list[Node]) -> Node:
    return nodes.pop()
