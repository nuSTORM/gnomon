from unittest import TestCase
import sys
import argparse
import exceptions

import GeneratorAction as GA

bad_verticies = ["UNIFORM",
                 [0,1],
                 [0,'hi']]
good_verticies = [[1,2,3],
                  [0.1,0.2,0.3],
                  [0,1.0,2]]
                 

class TestVlenfGeneratorAction(TestCase):
    def setUp(self):
        self.ga = GA.VlenfGeneratorAction()

    def test_log(self):
        self.ga.log.debug('test')

    def test_types_check3Vector(self):
        for bad_vertex in bad_verticies:
            with self.assertRaises(ValueError):
                self.ga.check3Vector(bad_vertex)
            
        for good_vertex in good_verticies:
            self.ga.check3Vector(good_vertex)

    def test_types_setVertex(self):
        for bad_vertex in bad_verticies:
            with self.assertRaises(ValueError):
                self.ga.setVertex(bad_vertex)

        for good_vertex in good_verticies:
            self.ga.setVertex(good_vertex)

    def test_setVertex(self):
        for good_vertex in good_verticies:
            self.ga.setVertex(good_vertex)
            self.assertEqual(good_vertex, self.ga.vertex)
        
class TestSingleParticleGeneratorAction(TestCase):
    def setUp(self):
        self.ga = GA.SingleParticleGeneratorAction()
        
    def test_types_setMomentum(self):
        for bad_vertex in bad_verticies:
            with self.assertRaises(ValueError):
                self.ga.setMomentum(bad_vertex)

        for good_vertex in good_verticies:
            self.ga.setMomentum(good_vertex)

    def test_types_setPID(self):
        with self.assertRaises(ValueError):
            self.ga.setPID('string')
        self.ga.setPID(-13)
        self.ga.setPID(13)

    def test_setMomentum(self):
        for good_vertex in good_verticies:
            self.ga.setMomentum(good_vertex)
            self.assertEqual(good_vertex, self.ga.momentum)

    def test_get_next_events(self):
        pass

    def test_GeneratePrimaries(self):
        pass

class TestGenieGeneratorAction(TestCase):
    def setUp(self):
        self.ga = GA.GenieGeneratorAction()
        
    def test_get_next_events(self):
        pass

    def test_GeneratePrimaries(self):
        pass


