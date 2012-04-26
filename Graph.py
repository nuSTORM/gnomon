import math

class Vertex():
    pass

class Edge():
    pass

class DAG():
    def __init__(self):
        self.graph = {}

    def CreateVertices(self, points):
        points.sort()
        
        graph = {}

        for z, x in points:
            graph[(z,x)] = {}

        return graph
            
    def GetVertices(self, graph):
        return graph.keys()

    def CreateDirectedEdges(self, points, graph):
        for z0, x0 in points:

            for z1, x1 in points:
                if z1 > z0:
                    dz = z1 - z0
                    dx = x1 - x0
                    graph[(z0,x0)][(z1, x1)] = math.hypot(dz, dx)
                    
        return graph

    def CutLongEdges(self, graph, threshold=50.0):
        new_graph = {}

        for key, endpoints in graph.iteritems():
            new_graph[key] = {}
            for endpoint, distance in endpoints.iteritems():
                if distance < threshold:
                    new_graph[key][endpoint] = distance
        
        return new_graph

    def LongestPath(self, graph):
        verts = self.GetVertices(graph)

        length_to = {}
        edge_to = {}

        for v in verts:
            edges = graph[v]
            for w in edges.keys():
                if w not in length_to:
                    length_to[w] = 0
                if v not in length_to:
                    length_to[v] = 0
                    
                if length_to[w] <= length_to[v] + edges[w]:
                    length_to[w] = length_to[v] + edges[w]
                    edge_to[w] = (v,w)

        print length_to
        print edge_to

        path = []
        current_point = 6
        while current_point != 0:
            v, w = edge_to[current_point]
            path.append((v,w))
            current_point = v

        print path

        
        
    def ProcessPoints(self, points):
        graph = CreateVertices(points)
        graph = CreateDirectedEdges(points, graph)
        graph = CutLongEdges(graph)
        
        i = 0

        for point in points:


            self.graph[point] = {}

            for vertex in graph.keys():
                z0, x0 = point
                z1, x1 = vertex

                if z1 == z0:
                    print 'same point, skip'
                
        


    
