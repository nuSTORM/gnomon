from unittest import TestCase
from Graph import DAG

points = [[5385,-1605],[5335,-1595], [5285,-1595]]

class TestDAG(TestCase):
    def setUp(self):
        self.dag = DAG()

    def test_CreateGetVertices(self):
        dag = DAG()
        graph = dag.CreateVertices(points)

        for z, x in points:
            self.assertIn((z, x), graph.keys())
            self.assertIn((z, x), dag.GetVertices(graph))
        print graph

    def test_CreateDirectedEdges(self):
        dag = DAG()
        graph = {(5385, -1605): {}, (5285, -1595): {}, (5335, -1595): {}}


        graph = dag.CreateDirectedEdges(points, graph)

    def test_CutLongEdges(self):
        graph = {(5385, -1605): {},
                 (5285, -1595): {(5385, -1605): 100.4987562112089, (5335, -1595): 50.0},
                 (5335, -1595): {(5385, -1605): 50.99019513592785}}

        dag = DAG()
        graph = dag.CutLongEdges(graph)
        self.assertNotIn((5385, -1605), graph[(5285, -1595)])

    def test_LongestPath(self):
        graph = {}

        edges = {}
        edges[(0,2)] = 2
        edges[(0,1)] = 1
        edges[(1,4)] = 2
        edges[(1,3)] = 1
        edges[(2,3)] = 2
        edges[(2,5)] = 2
        edges[(5,6)] = 2
        edges[(4,6)] = 1

        for value, weight in edges.iteritems():
            v, w = value
            if v not in graph:
                graph[v] = {}

            graph[v][w] = weight

        self.assertEqual([(5, 6), (2, 5), (0, 2)],
                         DAG().LongestPath(graph))

