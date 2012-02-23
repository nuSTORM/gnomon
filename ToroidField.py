import math
import Geant4 as G4

class ToroidField(G4.G4MagneticField):
    "My toroid Magnetic Field"

    def GetFieldValue(self, pos, time):
        r = math.sqrt( (pos.x)**2 + (pos.y )**2)

        bfield = G4.G4ThreeVector()

        B = -2  * G4.tesla # saturation                                            
        if r != 0.0:
            bfield.x = (pos.y / r) * B
            bfield.y = (pos.x / r) * B
        else:
            bfield.x = 0
            bfield.y = 0

        bfield.z = 0.

        return bfield
