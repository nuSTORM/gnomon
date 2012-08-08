"""Construct VLENF geometry"""


import Geant4 as G4
from SD import ScintSD
import MagneticField
from gnomon.Configuration import RUNTIME_CONFIG as rc
from Geant4 import G4Material


class IronBoxDetectorConstruction(G4.G4VUserDetectorConstruction):
    "Vlenf Detector Construction"

    def __init__(self):
        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sensitive_detector = None
        self.filename = "data/iron.gdml"

    def Construct(self):  # pylint: disable-msg=C0103                                                                                                                                                                                                      
        """Construct the VLENF from a GDML file"""
        # Parse the GDML                                                                                                                                                                                                                                   
        self.gdml_parser.Read(self.filename)
        self.world = self.gdml_parser.GetWorldVolume()

        print 'material', G4Material.GetMaterialTable()

        # Return pointer to world volume                                                                                                                                                                                                                                                                                                                                    
        return self.world

class VlenfDetectorConstruction(G4.G4VUserDetectorConstruction):
    "Vlenf Detector Construction"

    def __init__(self, field_polarity):
        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sensitive_detector = None
        self.filename = "data/iron_scint_bars.gdml"
        self.field_manager = None
        self.my_field = None
        self.field_polarity = field_polarity

    def __del__(self):
        pass

    def get_sensitive_detector(self):
        """Return the SD"""
        return self.sensitive_detector

    def Construct(self):  # pylint: disable-msg=C0103
        """Construct the VLENF from a GDML file"""
        # Parse the GDML
        self.gdml_parser.Read(self.filename)
        self.world = self.gdml_parser.GetWorldVolume()

        # Grab constants from the GDML <define>
        rc['layers'] = int(self.gdml_parser.GetConstant("layers"))
        rc['bars'] = int(self.gdml_parser.GetConstant("bars"))

        for name in ["width", "thickness_layer", "thickness_bar"]:
            rc[name] = self.gdml_parser.GetConstant(name)

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

        from Geant4 import G4Material
        print 'material', G4Material.GetMaterialTable()

        # Return pointer to world volume
        return self.world
