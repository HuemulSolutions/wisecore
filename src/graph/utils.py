from collections import deque
from rich import print

def topological_sort(sections):
    print(sections)
    graph     = {sec.id: [] for sec in sections}
    in_degree = {sec.id: 0  for sec in sections}

    for sec in sections:
        for d in sec.dependencies:
            dep_id = d["id"]
            if dep_id in graph:
                graph[dep_id].append(sec.id)
                in_degree[sec.id] += 1

    q = deque([nid for nid, deg in in_degree.items() if deg == 0])
    orden = []

    while q:
        u = q.popleft()
        orden.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)

    if len(orden) != len(sections):
        raise RuntimeError("Se detectó un ciclo en las dependencias de secciones")
    return orden