from unittest import TestCase
from gnomon import Configuration
from gnomon.DetectorConstruction import VlenfDetectorConstruction

Configuration.DEFAULT = Configuration.MockConfiguration

from gnomon import SD


class MockG4ThreeVector():
    x = 0
    y = 0
    z = 0


class TestSD(TestCase):
    def setUp(self):
        config_instance = Configuration.DEFAULT("mock")
        Configuration.GLOBAL_CONFIG = config_instance.get_configuration_dict()

        VlenfDetectorConstruction(field_polarity='+') # sets runtime geometry config
        self.sd = SD.ScintSD()

    def test_setEventNumber(self):
        for i in range(10):
            self.sd.setEventNumber(i)
            self.assertEqual(i, self.sd.event)

        with self.assertRaises(TypeError):
            self.sd.setEventNumber('string')

        with self.assertRaises(TypeError):
            self.sd.setEventNumber(3.4)

        with self.assertRaises(TypeError):
            self.sd.setEventNumber(None)

    def test_getNumberOfBars(self):
        self.assertEqual(self.sd.getNumberOfBars(), self.bars)

    def test_NumberOfLayers(self):
        self.assertEqual(self.sd.getNumberOfLayers(), self.layers)

    def test_getView(self):
        """Test getView

        At present, I don't do anything.  It gets passed in a Geant4
        LogicalVolume, which I guess we could instantiate?  Wait for bugs
        since testing with Geant4 objects is a pain.  See FAQ."""
        pass

    def test_ProcessHits(self):
        """Do nothing

        See FAQ about testing Geant4 interfaces"""
        pass

    def test_getMCHitBarPosition(self):
        values = [[389, 370, 'Y', 1400.909871, 1205.358881, 5040.0],
                  [391, 390, 'X', 1400.317685, 1204.113618, 5090.0],
                  [392, 370, 'Y', 1398.838643, 1201.865762, 5130.0],
                  [443, 399, 'Y', -644.785621, 1490.0, 6658.39763],
                  [443, 185, 'X', -640.0, 1479.008466, 6641.98194],
                  [408, 13, 'Y', -1651.58961, -2369.611604, 5605.78602],
                  [410, 84, 'X', -1650.566499, -2369.09055, 5660.0],
                  [44, 219, 'Y', 676.85137, -301.722366, -5316.1889],
                  [45, 317, 'X', 676.578609, -301.765424, -5290.0],
                  [46, 317, 'X', 675.80235, -301.908999, -5260.0],
                  [47, 317, 'X', 674.228821, -301.656047, -5230.0], ]

        bad_position = MockG4ThreeVector()  # wrong position, updated at end

        for value in values:
            layer_number = value[0]
            bar_number = value[1]
            view = value[2]
            position = MockG4ThreeVector()
            position.x = value[3]
            position.y = value[4]
            position.z = value[5]

            with self.assertRaises(AssertionError):
                self.sd.getMCHitBarPosition(layer_number, bar_number, view,
                    bad_position)

            self.sd.getMCHitBarPosition(
                layer_number, bar_number, view, position)
            bad_position = position  # this will be wrong position for next value
