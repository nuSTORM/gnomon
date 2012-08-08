"""The Tracking Action keeps track of pion decays and interactions"""

import logging
import math

import Geant4 as G4
from gnomon.Configuration import RUNTIME_CONFIG as rc


class LengthTrackingAction(G4.G4UserTrackingAction):
    """The tracking Action"""

    def __init__(self, pga=None):
        G4.G4UserTrackingAction.__init__(self)

    def PostUserTrackingAction(self, track):
        pdg_code = track.GetDefinition().GetPDGEncoding()
        if math.fabs(pdg_code) != 13:
            return

        # Be sure to clear rc['tracking'] in the append truth!
        if 'tracking' not in rc:
            rc['tracking'] = {}
        rc['tracking']['pdg_code'] = int(pdg_code)
        rc['tracking']['track_length'] = float(track.GetTrackLength())
        
        
