"""The EventAction is used by Geant4 to determine what to do before and after
each MC event."""

import logging

import Geant4 as G4
import Configuration

from processors.Digitize import VlenfSimpleDigitizer
from processors.Utils import Compactor

class VlenfEventAction(G4.G4UserEventAction):
    """The VLENF Event Action"""

    def __init__(self):
        """execute the constructor of the parent class G4UserEventAction"""
        G4.G4UserEventAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        
        self.config = Configuration.DEFAULT()

        self.processors = []
        #self.processors.append(VlenfSimpleDigitizer())
        self.processors.append(Compactor())

        #  (optionally) Used for telling SD to use bulk operations rather than
        #  individual commits.
        self.sd = None
        
    def BeginOfEventAction(self, event):
        """Executed at the beginning of an event, print hits"""
        self.log.debug("Beggining event %s", event.GetEventID())
        self.config.setEventNumber(event.GetEventID())

    def setSD(self, sd):
        self.sd = sd

    def EndOfEventAction(self, event):
        """Executed at the end of an event, do nothing"""
        self.log.info('Processed event %d', event.GetEventID())

        #  Trick to tell the sensitive detector to perform a bulk commit.
        if self.sd and self.sd.getUseBulkCommits():
            self.sd.bulkCommit()

        run_number = self.config.getRunNumber()
        for processor in self.processors:
            processor.FetchThenProcess(run_number, event.GetEventID())

        # Helps if we've deletected MChits
        #self.config.getCurrentDB().compact()

        
