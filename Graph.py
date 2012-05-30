import math

class Vertex():
    pass

class Edge():
    pass

class DAG():
    def __init__(self):
        self.graph = {}

    def CreateVertices(self, points):
        """
        Returns a dictionary object with keys that are 2tuples
        represnting a point.
        """
        points.sort()
        
        graph = {}

        for z, x in points:
            graph[(z,x)] = {}

        return graph
            
    def GetVertices(self, graph):
        """Return topologically sorted"""
        these_keys = graph.keys()
        these_keys.sort()
        return these_keys

    def CreateDirectedEdges(self, points, graph):
        """
        Take each key (ie. point) in the graph and for that point
        create an edge to every point downstream of it
        """
        for z0, x0 in points:
            for z1, x1 in points:
                if z1 > z0:
                    dz = z1 - z0
                    dx = x1 - x0

                    graph[(z0,x0)][(z1, x1)] = math.hypot(dz, dx)
                        
        return graph

    def CutLongEdges(self, graph, threshold=30):
        """ Remove all long edges"""
        new_graph = {}

        # For every initial point
        for key, endpoints in graph.iteritems():
            # Start fresh for end-points
            new_graph[key] = {}

            # For each endpoint, make sure distance isn't too long
            for endpoint, distance in endpoints.iteritems():
                if distance < threshold:
                    new_graph[key][endpoint] = distance

        print new_graph
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

        if len(length_to.keys()) == 0:
            return 0.0, []

        path = []
        current_point = None
        for key in length_to.keys():
            if current_point == None or length_to[key] > length_to[current_point]:
                current_point = key
        length_max = length_to[current_point]

        path.append(w)
        while 1:
            try:
                v, w = edge_to[current_point]
                path.append(v)
                current_point = v
            except:
                break  # ugly, but stops the loop?

        path.sort()
        return length_max, path

    
