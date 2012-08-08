"""The EventAction is used by Geant4 to determine what to do before and after
each MC event."""

import logging

import Geant4 as G4
import processors


class VlenfEventAction(G4.G4UserEventAction):
    """The VLENF Event Action"""

    def __init__(self, processor_names): # pga=None):
        """execute the constructor of the parent class G4UserEventAction"""
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
        """Executed at the beginning of an event, print hits"""
        self.log.debug("Beggining event %s", event.GetEventID())
        self.sd.setEventNumber(event.GetEventID())

    def setSD(self, sd):
        self.sd = sd

    def EndOfEventAction(self, event):
        """Executed at the end of an event, do nothing"""
        self.log.info('Processed event %d', event.GetEventID())

        docs = self.sd.getDocs()
        self.sd.clearDocs()

        for processor in self.processors:
            docs = processor.process(docs)
            if not docs:
                self.log.warning('%s did not return documents in process()!',
                                 processor.__class__.__name__)

    def shutdown(self):
        for processor in self.processors:
            processor.shutdown()
