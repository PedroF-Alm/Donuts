from collections import defaultdict

class Graph:

    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def BFS(self, s, visited, res):

        if visited is None:
            visited = [False] * (max(self.graph) + 1)

        queue = []

        queue.append(s)
        visited[s] = True

        while queue:

            s = queue.pop(0)
            res.append(s)
            
            for i in self.graph[s]:
                if not visited[i]:
                    queue.append(i)
                    visited[i] = True

    def getComponents(self):
        V = max(self.graph) + 1
        visited = [False] * V
        res = []

        for i in range(V):
            if not visited[i]:
                component = []
                self.BFS(i, visited, component)
                res.append(component)

        return res