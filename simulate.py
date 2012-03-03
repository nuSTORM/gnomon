#!/usr/bin/env python
# system libraries
import sys
import argparse
import logging
import os

# Geant4
temp = sys.stdout  # backup stdout
sys.stdout = open(os.devnull)  # make fake stdout
import Geant4 as G4  # Then silently import Geant4!
from Geant4 import HepRandom, gRunManager
from Geant4 import gTransportationManager, gApplyUICommand, mm
sys.stdout = temp  # Then return sys.stdout

# g4py
#import g4py.ExN03geom
import g4py.ExN03pl

# gnomon
import Configuration
import EventAction
import ToroidField
from GeneratorAction import GenieGeneratorAction
from GUI import VlenfApp
from DetectorConstruction import VlenfDetectorConstruction
import Logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate the VLENF')
    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
                        type=str, required=True)
    parser.add_argument('--number_events', help='how many events to simulate',
                        type=int, default=10)
    parser.add_argument('--run', help='run number',
                        type=int, default=1, required=True)

    group = parser.add_argument_group('Visualization', 'GUI or event display')
    group.add_argument('--gui', action='store_true')
    group.add_argument('--event_display', action='store_true')
    group.add_argument('--view', choices=['XY', 'ZY', 'ZX'], default='ZX')

    parser.add_argument('--pause', action='store_true',
                        help='pause after each event, require return')

    group = parser.add_argument_group('GeneratorAction', 'Input of particles to simulate')
    group1 = group.add_mutually_exclusive_group(required=True)
    group1.add_argument('--genie', '-g', action='store_true', help='Use Genie events')
    group1.add_argument('--particle', '-p', action='store_true', help='Use particle gun')

    group2 = group.add_mutually_exclusive_group(required=True)
    group2.add_argument('--vertex', metavar='N', type=float, nargs=3, help='vertex location (mm)')
    group2.add_argument('--uniform', '-u', action='store_true', help='uniform distribution')
    
    Logging.addLogLevelOptionToArgs(parser)  #  adds --log_level
    args = parser.parse_args()

    Logging.setupLogging(args.log_level)  # Console/file/stdout/stderr logs

    Configuration.run = args.run
    Configuration.name = args.name
    
    config = Configuration.CouchConfiguration(warn_if_db_exists = True)

    rand_engine = G4.Ranlux64Engine()
    HepRandom.setTheEngine(rand_engine)
    HepRandom.setTheSeed(20050830)

    detector = VlenfDetectorConstruction()
    gRunManager.SetUserInitialization(detector)

    exN03PL = g4py.ExN03pl.PhysicsList()
    gRunManager.SetUserInitialization(exN03PL)
    exN03PL.SetDefaultCutValue(1.0 * mm)
    exN03PL.SetCutsWithDefault()

    myEA = EventAction.VlenfEventAction()
    gRunManager.SetUserAction(myEA)

    pgPGA = GenieGeneratorAction()
    gRunManager.SetUserAction(pgPGA)

    fieldMgr = gTransportationManager.GetFieldManager()

    myField = ToroidField.ToroidField()
    fieldMgr.SetDetectorField(myField)
    fieldMgr.CreateChordFinder(myField)

# get the field right!

    gRunManager.Initialize()

    #  This is a trick that, if enabled, lets the event action notify the
    #  detector when the event is over.  This allows the sensitive detector
    #  to perform a bulk commit of 'mchit's to the event store.  It's meant
    #  to be an optimization since writing tons of small 'mchit's individually
    #  to the database is slow.
    #
    #  This can be disabled for conceptually clarify in SD.py
    sd = detector.getSensitiveDetector()
    myEA.setSD(sd)

    if args.event_display:
        gApplyUICommand("/vis/sceneHandler/create OGLSX OGLSX")
        gApplyUICommand("/vis/viewer/create OGLSX oglsxviewer")
        gApplyUICommand("/vis/drawVolume")
        gApplyUICommand("/vis/scene/add/trajectories")
        gApplyUICommand("/tracking/storeTrajectory 1")
        gApplyUICommand("/vis/scene/endOfEventAction accumulate")
        gApplyUICommand("/vis/scene/endOfRunAction accumulate")
        gApplyUICommand("/vis/viewer/select oglsxviewer")
        gApplyUICommand("/vis/scene/add/trajectories")

        if args.view == 'XY':
            gApplyUICommand("/vis/viewer/set/viewpointVector 0 0 -1")
        elif args.view == 'ZY':
            gApplyUICommand("/vis/viewer/set/viewpointVector -1 0 0")
        elif args.view == 'ZX':
            gApplyUICommand("/vis/viewer/set/viewpointVector -1 100000 0")

    if args.gui:
        app = VlenfApp()
        app.mainloop()

    if args.pause:
        for i in range(args.number_events):
            gRunManager.BeamOn(1)
            raw_input()
    else:
        gRunManager.BeamOn(args.number_events)
