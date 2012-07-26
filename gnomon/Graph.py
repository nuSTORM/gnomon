import math

distance_threshold = 0.1
bar_width = 10.0

from pygraph.classes.digraph import digraph
from pygraph.algorithms import critical
from pygraph.algorithms.searching import breadth_first_search
from pygraph.algorithms import minmax
from pygraph.algorithms import accessibility


class Graph():
    def __init__(self):
        self.graph = {}

    def FindParentNode(self, gr):
        transitive_closure = accessibility.accessibility(gr)

        most_accesisible_node = None
        for node_in, nodes_out in transitive_closure.iteritems():
            if most_accesisible_node is None:
                most_accesisible_node = node_in

            max_value = len(transitive_closure[most_accesisible_node])
            this_value = len(nodes_out)

            if this_value > max_value:
                most_accesisible_node = node_in

        return most_accesisible_node

    def CreateVertices(self, points):
        """
        Returns a dictionary object with keys that are 2tuples
        represnting a point.
        """
        gr = digraph()

        for z, x, Q in points:
            node = (z, x, Q)
            gr.add_nodes([node])

        return gr

    def CreateDirectedEdges(self, points, gr, layer_width):
        """
        Take each key (ie. point) in the graph and for that point
        create an edge to every point downstream of it where the weight
        of the edge is the tuple (distance, angle)
        """
        for z0, x0, Q0 in points:
            for z1, x1, Q1 in points:
                dz = z1 - z0  # no fabs because we check arrow direction
                if dz > 0.0:  # make sure arrow in right direction
                    if dz - layer_width < distance_threshold:  # only adjacents
                        dx = math.fabs(x1 - x0)

                        angle = math.atan(dx / dz)

                        if dx > 5 * bar_width:
                            continue

                        # Weights are negative to in order to use shortest path
                        # algorithms on the graph.
                        weight = -1 * math.hypot(dz, dx)

                        edge = ((z0, x0, Q0), (z1, x1, Q1))

                        gr.add_edge(edge, wt=weight)

        # Ensure that it is already transitively reduced
        assert len(critical.transitive_edges(gr)) == 0

        return gr

    def GetFarthestNode(self, gr, node):
        """node is start node"""
        # Remember: weights are negative
        st, distance = minmax.shortest_path_bellman_ford(gr, node)

        nodes = distance.keys()

        # Find the farthest node, which is end of track
        min_key = None
        for key, value in distance.iteritems():
            if min_key is None or value < distance[min_key]:
                min_key = key

        return min_key

    def NegateGraph(self, gr):
        for edge in gr.edges():
            weight = gr.edge_weight(edge)
            gr.set_edge_weight(edge, -1 * weight)
        return gr

    def ComputeLongestPath(self, gr, parent_node):
        parent_node = self.FindParentNode(gr)

        farthest_node = self.GetFarthestNode(gr, parent_node)

        gr = self.NegateGraph(gr)
        st, distance = minmax.shortest_path_bellman_ford(gr, parent_node)
        gr = self.NegateGraph(gr)

        max_distance = distance[farthest_node]

        # Then swim back to the parent node.  Record the path.
        node_list = [farthest_node]
        i = 0
        while parent_node not in node_list:
            node_list.append(st[node_list[-1]])

            i += 1
            if i > 10000:
                print node_list
                raise ValueError()

        #  Grab doublets
        node_list2 = []
        for node1 in node_list:
            for node2 in gr.nodes():
                z1, x1, Q1 = node1
                z2, x2, Q2 = node2
                dx = math.fabs(x1 - x2)

                if z1 == z2 and math.fabs(dx - bar_width) < distance_threshold:
                    node_list2.append(node2)

        for node in node_list + node_list2:
            if node:
                gr.del_node(node)

        node_list = [x for x in node_list if x is not None]
        return node_list, max_distance, gr
