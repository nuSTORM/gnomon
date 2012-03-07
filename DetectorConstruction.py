import Geant4 as G4
from SD import ScintSD

import MagneticField

class VlenfDetectorConstruction(G4.G4VUserDetectorConstruction):
    "Vlenf Detector Construction"

    def __init__(self):
        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sensitive_detector = None
        self.filename = "gdml/iron_scint_bars.gdml"

    def __del__(self):
        pass

    def getSensitiveDetector(self):
        """Return the SD"""
        return self.sensitive_detector

    def Construct(self):
        """Construct the VLENF from a GDML file"""
        # Parse the GDML
        self.gdml_parser.Read(self.filename)
        self.world = self.gdml_parser.GetWorldVolume()

        # Grab constants from the GDML <define>
        layers = int(self.gdml_parser.GetConstant("layers"))
        bars = int(self.gdml_parser.GetConstant("bars"))
        width = self.gdml_parser.GetConstant("width")
        thickness_layer = self.gdml_parser.GetConstant("thickness_layer")
        thickness_bar = self.gdml_parser.GetConstant("thickness_bar")

        # Create sensitive detector
        self.sensitive_detector = ScintSD(layers, bars, width,
                                          thickness_layer, thickness_bar)

        # Get logical volume for X view, then attach SD
        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(1)
        assert lv.GetName() == "ScintillatorBarX"
        lv.SetSensitiveDetector(self.sensitive_detector)

        # Get logical volume for Y view, then attach SD
        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(2)
        assert lv.GetName() == "ScintillatorBarY"
        lv.SetSensitiveDetector(self.sensitive_detector)

        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(0)
        assert lv.GetName() == "SteelPlane"
        fieldMgr = G4.G4FieldManager()
        myField = MagneticField.WandsToroidField()
        fieldMgr.SetDetectorField(myField)
        fieldMgr.CreateChordFinder(myField)

        # Return pointer to world volume
        return self.world
