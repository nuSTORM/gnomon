"""The Tracking Action keeps track of pion decays and interactions"""

import logging
import math

import Geant4 as G4
import Configuration

def ConvertG4ThreeVectorToDict(g4vector):
    dictvector = {}
    dictvector['x'] = g4vector.x
    dictvector['y'] = g4vector.y
    dictvector['z'] = g4vector.z
    return dictvector

class TrackingAction(G4.G4UserTrackingAction):
    """The tracking Action"""

    def __init__(self, pga=None):
        """execute the constructor of the parent class G4UserEventAction"""
        G4.G4UserTrackingAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        
        self.config = Configuration.DEFAULT()
        self.info = {}

    def FetchThenClear(self):
        temp = self.info
        self.info = {}
        return temp

    def PreUserTrackingAction(self, track):
        cp = track.GetCreatorProcess()
        if not cp:
            return
        
        cp_name = cp.GetProcessName()

        if str(cp_name) != 'Decay':
            return

        pdg_code = track.GetDefinition().GetPDGEncoding()
        if math.fabs(pdg_code) != 13:
            return

        if 'decay_to_muon' not in self.info:
            self.info['decay_to_muon'] = []

        this_info = {}

        pos = ConvertG4ThreeVectorToDict(track.GetVertexPosition())
        this_info['vertex'] = pos

        mom = ConvertG4ThreeVectorToDict(track.GetMomentum())
        this_info['momentum'] = mom
        
        this_info['pdg_code'] = int(pdg_code)
        
        self.info['decay_to_muon'].append(this_info)

    def PostUserTrackingAction(self, track):
        pdg_code = track.GetDefinition().GetPDGEncoding()
        if math.fabs(pdg_code) != 211:
            return

        if 'pion_info' not in self.info:
            self.info['pion_info'] = []

        this_info = {}
        this_info['pdg_code'] = int(pdg_code)
        this_info['track_length'] = float(track.GetTrackLength())

        self.info['pion_info'].append(this_info)


            



        
        
