"""The EventAction is used by Geant4 to determine what to do before and after
each MC event."""

import Geant4 as G4
import Configuration
import Digitize

class VlenfEventAction(G4.G4UserEventAction):
    """The VLENF Event Action"""

    def __init__(self):
        """execute the constructor of the parent class G4UserEventAction"""
        G4.G4UserEventAction.__init__(self)
        
        self.config = Configuration.DEFAULT()
        self.couch = self.config.getCouchDB()

        self.sd = None

    def SetSensitiveDetector(self, sd):
        """Store a sensitive detector, which is used for grabbing hits in the
        EndOfEventAction"""
        self.sd = sd

    def BeginOfEventAction(self, event):
        """Executed at the beginning of an event, print hits"""
        print "*** current event (BEA)=", event.GetEventID()
        self.db_name = 'mc_hit_%d_%d' % (self.run_number, event.GetEventID())

        self.sd.setNextEventDBName(self.db_name)

    def EndOfEventAction(self, event):
        """Executed at the end of an event, do nothing"""
        print "*** current event (EEA)=", event.GetEventID()
        #hits = self.sd.getHits()

        db = self.couch[self.db_name]

        # index is layer, bar
        events = {}
        
        for key in db:
            doc = db[key]
            i = doc['layer']
            j = doc['bar']

            if (i,j) not in events:
                events[(i,j)] = []

            events[(i,j)].append(dict(doc))

        print events
