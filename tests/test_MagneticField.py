from unittest import TestCase
from gnomon import MagneticField


class MockG4ThreeVector():
    x = 0
    y = 0
    z = 0


class TestWandsToroidField(TestCase):
    def setUp(self):
        self.field_minus = MagneticField.WandsToroidField('-')
        self.field_plus = MagneticField.WandsToroidField('+')
        self.fields = [self.field_minus, self.field_plus]

    def test_PhenomModel(self):
        for field in self.fields:
            with self.assertRaises(ValueError):
                field.PhenomModel(0)

            with self.assertRaises(ValueError):
                field.PhenomModel(-1)

            field.PhenomModel(1)

    def test_GetFieldValue(self):
        for field in self.fields:
            pos = MockG4ThreeVector()
            vector = field.GetFieldValue(pos, 0)
            self.assertEqual(vector.x, 0)
            self.assertEqual(vector.y, 0)
            self.assertEqual(vector.z, 0)

            pos.x = 1
            vector = field.GetFieldValue(pos, 0)

        pos = MockG4ThreeVector()
        pos.x = 1
        pos.y = 2
        pos.z = 3
        vector_plus = self.field_plus.GetFieldValue(pos, 0)
        vector_minus = self.field_minus.GetFieldValue(pos, 0)

        self.assertAlmostEqual(vector_plus.x, -1 * vector_minus.x)
        self.assertAlmostEqual(vector_plus.y, -1 * vector_minus.y)
        self.assertAlmostEqual(vector_plus.z, -1 * vector_minus.z)
