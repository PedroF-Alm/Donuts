from collections import defaultdict

# This class represents a directed graph
# using adjacency list representation
class Graph:

    # Constructor
    def __init__(self):

        # Default dictionary to store graph
        self.graph = defaultdict(list)

    # Function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)

    # Function to print a BFS of graph
    def BFS(self, s, visited, res):

        # Mark all the vertices as not visited
        if visited is None:
            visited = [False] * (max(self.graph) + 1)

        # Create a queue for BFS
        queue = []

        # Mark the source node as
        # visited and enqueue it
        queue.append(s)
        visited[s] = True

        while queue:

            # Dequeue a vertex from
            # queue and print it
            s = queue.pop(0)
            res.append(s)
            
            # Get all adjacent vertices of the
            # dequeued vertex s.
            # If an adjacent has not been visited,
            # then mark it visited and enqueue it
            for i in self.graph[s]:
                if not visited[i]:
                    queue.append(i)
                    visited[i] = True

    # BFS for all components (handles disconnected graphs)
    def getComponents(self):
        V = max(self.graph) + 1
        visited = [False] * V
        res = []

        # Loop through all vertices
        # to handle all components
        for i in range(V):
            if not visited[i]:
                component = []
                self.BFS(i, visited, component)
                res.append(component)

        return res