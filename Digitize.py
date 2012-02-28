"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""

import Geant4 as G4
import Configuration

class VlenfSimpleDigitizer():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""
    
    def __init__(self):
        self.config = Configuration.DEFAULT()
        self.couch = self.config.getCouchDB()

        self.sd = None


    def FetchThenProcess(self, run, event):
        self.db_name = 'mc_hit_%d_%d' % (run, event)
        db = self.couch[self.db_name]

        hits = {}
        for key in db:
            doc = db[key]
            i = doc['layer']
            j = doc['bar']

            if (i,j) not in hits:
                hits[(i,j)] = []
            
            hits[(i,j)].append(dict(doc))

        self.Process(hits)

    def Process(self, hits):
        print hits

