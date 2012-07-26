"""The EventAction is used by Geant4 to determine what to do before and after
each MC event."""

import logging

import Geant4 as G4
import Configuration
from Digitizer import VlenfSimpleDigitizer
import Fitter
from Truth import AppendTruth
from DataManager import CouchManager

class VlenfEventAction(G4.G4UserEventAction):
    """The VLENF Event Action"""

    def __init__(self, pga=None):
        """execute the constructor of the parent class G4UserEventAction"""
        G4.G4UserEventAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.processors = []
        self.processors.append(VlenfSimpleDigitizer())
        self.processors.append(Fitter.EmptyTrackFromDigits())



        self.processors.append(Fitter.ExtractTracks())
        self.processors.append(Fitter.VlenfPolynomialFitter())
        self.processors.append(Fitter.EnergyDeposited())
        self.processors.append(AppendTruth(pga))
        self.processors.append(CouchManager())

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
            docs = processor.Process(docs)

    def Shutdown(self):
        for processor in self.processors:
            processor.Shutdown()
