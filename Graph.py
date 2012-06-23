import math

distance_threshold = 0.1
angle_threshold = 3 * ((13.6/200) * math.sqrt(4.0/3.52))

from pygraph.classes.digraph import digraph
from pygraph.algorithms import critical
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms import minmax

class Graph():
    def __init__(self):
        self.graph = {}

        self.is_mst = False
        self.is_dag = False

    def FindParentNode(self, gr):
        minimum_node = None

        for node in gr.nodes():
            if minimum_node == None or node[0] < minimum_node[0]:
                minimum_node = node
        return minimum_node

    def CreateVertices(self, points):
        """
        Returns a dictionary object with keys that are 2tuples
        represnting a point.
        """
        gr = digraph()

        for z, x in points:
            node = (z,x)
            gr.add_nodes([node])

        return gr
            
    def GetVertices(self, graph):
        """Return topologically sorted"""
        these_keys = graph.keys()
        these_keys.sort()
        return these_keys

    def CreateDirectedEdges(self, points, gr, layer_width):
        """
        Take each key (ie. point) in the graph and for that point
        create an edge to every point downstream of it where the weight
        of the edge is the tuple (distance, angle)
        """
        for z0, x0 in points:
            for z1, x1 in points:
                dz = z1 - z0
                if dz > 0.0:  # make sure arrow in right direction
                    if dz - layer_width < distance_threshold:  # only adjacents
                        dx = x1 - x0

                        angle = math.atan(dx/dz)

                        if dx > 20:
                            continue

                        # Weights are negative to in order to use shortest path
                        # algorithms on the graph.
                        weight = -1 * math.hypot(dz, dx)

                        edge = ((z0,x0),(z1, x1))
                        
                        gr.add_edge(edge, wt=weight)

        # Ensure that it is already transitively reduced
        assert len(critical.transitive_edges(gr)) == 0
        
        return gr


    def FindMST(self, gr):
        """Minimal spaning tree"
        parent_node = self.FindParentNode(gr)
        
        st, order = breadth_first_search(gr, root=min)
        gst = digraph()
        gst.add_spanning_tree(st)

        return gst

    def LongestPath(self, gr):
        parent_node = self.FindParentNode(gr)
        
        # Remember: weights are negative
        st, distance = minmax.shortest_path_bellman_ford(gr, parent_node)
        print 'dist', distance

        gst = digraph()
        gst.add_spanning_tree(st)
        return gst

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

    
