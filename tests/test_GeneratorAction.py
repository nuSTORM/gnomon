from unittest import TestCase
from gnomon import GeneratorAction as GA

bad_verticies = [[0, 1],
                 'some_other_string',
                 [0, 'hi']]
good_verticies = [[1, 2, 3],
                  [0.1, 0.2, 0.3],
                  [0, 1.0, 2]]

class TestCompositeZ(TestCase):
    def setUp(self):
        config = {}
        config['layers'] = 444
        config['thickness_layer'] = 40.0
        config['thickness_bar'] = 10.0
        config['density_iron'] = 7.87
        config['density_scint'] = 1.06

        self.max_size = config['layers'] * config['thickness_layer'] / 2
        self.dist = GA.composite_z(config)


    def test_rvs_range(self):
        for i in range(1000):
            rand_val = self.dist.rvs()
            error_string = "%f %f" % (rand_val, self.max_size)
            assert -self.max_size < rand_val < self.max_size, error_string


"""class TestVlenfGeneratorAction(TestCase):
    def setUp(self):
        self.ga = GA.GnomonGeneratorAction()

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
        self.ga.setVertex('uniform')

    def test_setVertex(self):
        for good_vertex in good_verticies:
            self.ga.setVertex(good_vertex)
            self.assertEqual(good_vertex, self.ga.vertex)

        self.ga.setVertex('uniform')
        self.assertEqual('uniform', self.ga.vertex)


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
"""
