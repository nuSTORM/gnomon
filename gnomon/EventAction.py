"""The EventAction is used by Geant4 to determine what to do before and after
each MC event."""

import logging

import Geant4 as G4
import processors


class EventAction(G4.G4UserEventAction):
    """A Geant4 interface that subclasses G4UserEventAction and runs processors over Geant4 events"""

    def __init__(self, processor_names):  # pga=None):
        G4.G4UserEventAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.processors = []

        for name in processor_names:
            try:
                my_class = processors.lookupProcessor(name)
                self.processors.append(my_class())
            except:
                self.log.error('Failed loading processor %s' % name)
                raise

        # used to fetch mchits, only way given geant
        self.sd = None

    def BeginOfEventAction(self, event):
        """Save event number"""
        self.log.info("Simulating event %s", event.GetEventID())
        self.sd.setEventNumber(event.GetEventID())

    def setSD(self, sd):
        """Hook to the sensitive detector class

        User for fetching hits from sensitive detector to pass to processor loop"""
        self.sd = sd

    def EndOfEventAction(self, event):
        """At the end of an event, grab sensitive detector hits then run processor loop"""
        self.log.debug('Processesing simulated event %d', event.GetEventID())

        docs = self.sd.getDocs()
        self.sd.clearDocs()

        for processor in self.processors:
            docs = processor.process(docs)
            if not docs:
                self.log.warning('%s did not return documents in process()!',
                    processor.__class__.__name__)


    def shutdown(self):
        """Shutdown each processor"""
        for processor in self.processors:
            processor.shutdown()
