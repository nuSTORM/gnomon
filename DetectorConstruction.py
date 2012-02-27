import Geant4 as G4
from SD import ScintSD

class VlenfDetectorConstruction(G4.G4VUserDetectorConstruction):
    "Vlenf Detector Construction"

    def __init__(self):
        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sd = None

    def __del__(self):
        pass

    def getSD(self):
        return self.sd

    def Construct(self):
        filename = "gdml/iron_scint_bars.gdml"
        self.gdml_parser.Read(filename)
        self.world = self.gdml_parser.GetWorldVolume()

        for i in range(6):
            print i, G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(i).GetName()

        layers = self.gdml_parser.GetConstant("layers")
        bars = self.gdml_parser.GetConstant("bars")
        width = self.gdml_parser.GetConstant("width")
        thickness_layer = self.gdml_parser.GetConstant("thickness_layer")
        thickness_bar = self.gdml_parser.GetConstant("thickness_bar")

        self.sd = ScintSD(layers, bars, width, thickness_layer, thickness_bar)

        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(1)
        assert lv.GetName() == "ScintillatorBarX"
        print 'using sd as %s' % lv.GetName()
        lv.SetSensitiveDetector(self.sd)

        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(2)
        assert lv.GetName() == "ScintillatorBarY"
        lv.SetSensitiveDetector(self.sd)

        return self.world
