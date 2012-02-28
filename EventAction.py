"""The EventAction is used by Geant4 to determine what to do before and after
each MC event."""

import Geant4 as G4
import Configuration
from Digitize import VlenfSimpleDigitizer

class VlenfEventAction(G4.G4UserEventAction):
    """The VLENF Event Action"""

    def __init__(self):
        """execute the constructor of the parent class G4UserEventAction"""
        G4.G4UserEventAction.__init__(self)
        
        self.config = Configuration.DEFAULT()

        self.processors = []
        self.processors.append(VlenfSimpleDigitizer())
        
    def BeginOfEventAction(self, event):
        """Executed at the beginning of an event, print hits"""
        print "*** current event (BEA)=", event.GetEventID()
        self.config.setEventNumber(event.GetEventID())

    def EndOfEventAction(self, event):
        """Executed at the end of an event, do nothing"""
        print "*** current event (EEA)=", event.GetEventID()

        run_number = self.config.getRunNumber()
        for processor in self.processors:
            processor.FetchThenProcess(run_number, event.GetEventID())

        # Helps if we've deletected MChits
        self.config.getCurrentDB().compact()

        
