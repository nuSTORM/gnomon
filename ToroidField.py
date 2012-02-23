import math
import Geant4 as G4


class ToroidField(G4.G4MagneticField):
    "Toroid Field from Bob Wands simulation parameterization"

    def __init__(self, focus='-'):
        G4.G4MagneticField.__init__(self)
        if focus == '+':
            self.sign = 1
        elif focus == '-':
            self.sign = -1
        else:
            raise ValueError

    def PhenomModel(self, r, B0=1.53, B1=0.032, B2=0.64, H=0.28):
        field = B0 + B1 / r + B2 * math.exp(-1 * H / r)
        return field * G4.tesla

    def GetFieldValue(self, pos, time):
        # From Bob Wands, 1 cm plate, Jan. 30
        r = math.sqrt(pos.x ** 2 + pos.y ** 2)

        # Paremeterization from talk above
        bfield = G4.G4ThreeVector()

        B = self.sign * self.PhenomModel(r)
        if r != 0.0:
            bfield.x = (pos.y / r) * B
            bfield.y = (pos.x / r) * B
        else:
            bfield.x = 0
            bfield.y = 0

        bfield.z = 0.

        return bfield
