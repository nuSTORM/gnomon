"""Construct a detector within Geant4

This module deals with creating detectors (geometries, sensitive detectors, etc.) and interfacing them with Geant4.
There is, for example, a class that loads geometries from GDML.

TODO: can box construction and calorimeter construction be superclassed?  Ideally with superclass handling the Geant4
interface and the subclasses tweaking the detector for their specific need.
"""

import os
import logging
import Geant4 as G4
from SensitiveDetector import ScintSD
import MagneticField
import gnomon.Configuration as Configuration
from gnomon.Configuration import RUNTIME_CONFIG as rc


class BoxDetectorConstruction(G4.G4VUserDetectorConstruction):
    """Create a cuboid geometry of uniform material

     Useful for testing particle interactions with uniform materials"""

    def __init__(self, name):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sensitive_detector = None

        self.config = Configuration.GLOBAL_CONFIG

        self.filename = os.path.join(self.config['data_dir'], name)

    def Construct(self):  # pylint: disable-msg=C0103
        """Construct a cuboid from a GDML file without sensitive detector"""
        # Parse the GDML
        self.gdml_parser.Read(self.filename)
        self.world = self.gdml_parser.GetWorldVolume()

        self.log.info("Materials:")
        self.log.info(G4.G4Material.GetMaterialTable())

        # Return pointer to world volume
        return self.world


class MagIronSamplingCaloDetectorConstruction(G4.G4VUserDetectorConstruction):
    """Create a magnetized iron sampling calorimeter"""

    def __init__(self, field_polarity):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sensitive_detector = None

        self.config = Configuration.GLOBAL_CONFIG
        self.filename = os.path.join(self.config['data_dir'],
            'iron_scint_bars.gdml')
        self.field_manager = None
        self.my_field = None
        self.field_polarity = field_polarity

        self.gdml_parser.Read(self.filename)

        # Grab constants from the GDML <define>
        rc['layers'] = int(self.gdml_parser.GetConstant("layers"))
        rc['bars'] = int(self.gdml_parser.GetConstant("bars"))
        for name in ["width", "thickness_layer", "thickness_bar",
                     "density_scint", "density_iron"]:
            rc[name] = self.gdml_parser.GetConstant(name)

        det_width = rc['width'] * rc['bars']
        iron_volume = det_width * det_width * (rc['layers'] / 2 * (rc['thickness_layer'] - rc['thickness_bar']))
        scint_volume = det_width * det_width * (rc['layers'] / 2 * rc['thickness_bar'])
        self.mass = iron_volume * rc['density_iron'] + scint_volume * rc['density_scint']
        self.mass /= 10 ** 3 # mm^2 -> cm^3, density in /cm^3 but distances in mm
        self.log.info("Mass [g]: %f" % self.mass)

    def __del__(self):
        pass

    def get_sensitive_detector(self):
        """Return the SD"""
        return self.sensitive_detector

    def Construct(self):  # pylint: disable-msg=C0103
        """Construct nuSTORM from a GDML file"""
        # Parse the GDML
        self.world = self.gdml_parser.GetWorldVolume()

        # Create sensitive detector
        self.sensitive_detector = ScintSD()

        # Get logical volume for X view, then attach SD
        my_lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(1)
        assert my_lv.GetName() == "ScintillatorBarX"
        my_lv.SetSensitiveDetector(self.sensitive_detector)

        # Get logical volume for Y view, then attach SD
        my_lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(2)
        assert my_lv.GetName() == "ScintillatorBarY"
        my_lv.SetSensitiveDetector(self.sensitive_detector)

        my_lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(0)
        assert my_lv.GetName() == "SteelPlane"

        # field
        self.field_manager = G4.G4FieldManager()
        self.my_field = MagneticField.WandsToroidField(self.field_polarity)
        self.field_manager.SetDetectorField(self.my_field)
        self.field_manager.CreateChordFinder(self.my_field)
        my_lv.SetFieldManager(self.field_manager, False)

        self.log.info("Materials:")
        self.log.info(G4.G4Material.GetMaterialTable())

        # Return pointer to world volume
        return self.world
