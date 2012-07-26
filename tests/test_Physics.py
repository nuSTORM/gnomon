from unittest import TestCase
import sys
import argparse
import exceptions

import logging  # python's
import Logging  # gnomon's


class TestLogging(TestCase):
    def setUp(self):
        pass

    def test_exist_getLogLevels(self):
        bad_level_name = 'blarg'
        l = logging.getLogger(bad_level_name)

        with self.assertRaises(ValueError):
            l.setLevel(bad_level_name)

        for level_name in Logging.getLogLevels():
            l = logging.getLogger(level_name)
            l.setLevel(level_name)

#
import sys
import argparse
import logging
import os
import random

# Geant4
temp = sys.stdout  # backup stdout
sys.stdout = open(os.devnull)  # make fake stdout
import Geant4 as G4  # Then silently import Geant4!
from Geant4 import HepRandom, gRunManager
from Geant4 import gTransportationManager, gApplyUICommand, mm
sys.stdout = temp  # Then return sys.stdout

# gnomon
import Configuration
import EventAction
import TrackingAction
import GeneratorAction
from DetectorConstruction import VlenfDetectorConstruction
import Logging

log = None  # Logger for this file


class TestTrackingAction(G4.G4UserTrackingAction):
    def __init__(self, pid_of_interest):
        G4.G4UserTrackingAction.__init__(self)
        self.event_lengths = []

        self.pid_of_interest = pid_of_interest

    def EventLengths(self):
        temp = self.event_lengths
        self.event_lengths = []
        return temp

    def PostUserTrackingAction(self, track):
        pdg_code = track.GetDefinition().GetPDGEncoding()

        if not track.GetCreatorProcess():
            assert pdg_code == self.pid_of_interest
            self.event_lengths.append(track.GetTrackLength())

            print track.GetVertexPosition(), track.GetPosition()

if __name__ == "__main__":
    random.seed()

    Configuration.run = random.randint(1, sys.maxint)
    Configuration.name = 'physics_test'

    config = Configuration.DEFAULT()

    rand_engine = G4.Ranlux64Engine()
    HepRandom.setTheEngine(rand_engine)

    seed = random.randint(1, 65536)
    HepRandom.setTheSeed(0)

    detector = VlenfDetectorConstruction(field_polarity='0')
    gRunManager.SetUserInitialization(detector)

    exN03PL = G4.G4physicslists.QGSP_BERT()
    gRunManager.SetUserInitialization(exN03PL)
    exN03PL.SetDefaultCutValue(1.0 * mm)
    exN03PL.SetCutsWithDefault()

    pga = GeneratorAction.SingleParticleGeneratorAction()
    pga.setVertex([0, 0, 0])

    pga.setMomentum([0, 0, 3000])

    my_pid = 211
    pga.setPID(my_pid)

    gRunManager.SetUserAction(pga)

    myTA = TestTrackingAction(my_pid)
    gRunManager.SetUserAction(myTA)

    myEA = EventAction.VlenfEventAction(pga, myTA)
    gRunManager.SetUserAction(myEA)

    gRunManager.Initialize()

    #  This is a trick that, if enabled, lets the event action notify the
    #  detector when the event is over.  This allows the sensitive detector
    #  to perform a bulk commit of 'mchit's to the event store.  It's meant
    #  to be an optimization since writing tons of small 'mchit's individually
    #  to the database is slow.
    sd = detector.getSensitiveDetector()
    myEA.setSD(sd)

    gRunManager.BeamOn(10)

    myEA.Shutdown()

    x = myTA.EventLengths()
    print len(x)
    print x
    print len(x)
