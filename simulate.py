#!/usr/bin/env python
# system libraries
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

# g4py
#import g4py.ExN03geom
import g4py.ExN03pl

# gnomon
import Configuration
import EventAction
import GeneratorAction
from DetectorConstruction import VlenfDetectorConstruction
import Logging

log = None  #  Logger for this file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate the VLENF')
    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
                        type=str, required=True)
    parser.add_argument('--events', help='how many events to simulate',
                        type=int, default=10)
    parser.add_argument('--run', help='run number (random if 0)',
                        type=int, default=0)
    parser.add_argument('--seed', help='random seed, 0 means set to clock',
                        type=int, default=0)
    parser.add_argument('--logfileless', action='store_true',
                        help='this will disable writing out a log file')
    parser.add_argument('--polarity', choices=['+','-'], default='+', help='field polarity')

    group = parser.add_argument_group('Visualization', 'event display')
    group.add_argument('--display', action='store_true', help='event display')
    group.add_argument('--view', choices=['XY', 'ZY', 'ZX'], default='ZX')

    parser.add_argument('--pause', action='store_true',
                        help='pause after each event, require return')

    group = parser.add_argument_group('GeneratorAction', 'Input of particles to simulate')
    group.add_argument('--momentum', metavar='N', type=float, nargs=3, help='momentum MeV/c (requires particle)')
    group.add_argument('--pid', type=int, help='Geant4 particle number (requires particle, default=-13)')

    group1 = group.add_mutually_exclusive_group()
    group1.add_argument('--genie', '-g', type=str, help="genie")

    group1.add_argument('--particle', '-p', action='store_true', help='Use particle gun')

    group2 = group.add_mutually_exclusive_group(required=True)
    group2.add_argument('--vertex', metavar='N', type=float, nargs=3, help='vertex location (mm)')
    group2.add_argument('--uniform', '-u', action='store_true', help='uniform distribution')
    
    Logging.addLogLevelOptionToArgs(parser)  #  adds --log_level
    args = parser.parse_args()

    Logging.setupLogging(args.log_level, args.name, logfileless=args.logfileless)
    log = logging.getLogger('root').getChild('simulate')
    log.debug('Commandline args: %s', str(args))

    random.seed()

    if args.run == 0:
        Configuration.run = random.randint(1, sys.maxint)
        log.warning('Using random run number %d since none specified', Configuration.run)
    else:
        Configuration.run = args.run
    Configuration.name = args.name
    
    config = Configuration.DEFAULT()

    rand_engine = G4.Ranlux64Engine()
    HepRandom.setTheEngine(rand_engine)
    seed = args.seed
    if seed == 0:
        seed = random.randint(1, 65536)
        log.warning('Using random seed %d', seed)
    else:
        log.info('Using seed %d', seed)
    HepRandom.setTheSeed(seed)

    detector = VlenfDetectorConstruction(field_polarity=args.polarity)
    gRunManager.SetUserInitialization(detector)

    exN03PL = g4py.ExN03pl.PhysicsList()
    gRunManager.SetUserInitialization(exN03PL)
    exN03PL.SetDefaultCutValue(1.0 * mm)
    exN03PL.SetCutsWithDefault()

    myEA = EventAction.VlenfEventAction()
    gRunManager.SetUserAction(myEA)
    
    #
    #  Generator actions
    #
    if args.particle:
        pga = GeneratorAction.SingleParticleGeneratorAction()
    else:
        if not args.genie:
            log.warning('No generator action set, assuming GenieGeneratorAction')
        pga = GeneratorAction.GenieGeneratorAction(args.genie)
        
    if args.vertex:
        pga.setVertex(args.vertex)
    elif args.uniform:
        pga.setVertex('uniform')
        #raise NotImplementedError('Uniform distribution not implemented')

    if args.momentum:
        if args.genie:
            log.error('Momentum cannot be set if using GenieGeneratorAction, ignoring...')
        else:
            pga.setMomentum(args.momentum)

    if args.pid:
        if args.genie:
            log.error('PID cannot be set if using GenieGeneratorAction, ignoring...')
        else:
            pga.setPID(args.pid)

    gRunManager.SetUserAction(pga)

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

    if args.display:
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

    #import GUI
    #app = GUI.VlenfApp()
    #app.mainloop()

    if args.pause:
        for i in range(args.events):
            gRunManager.BeamOn(1)
            raw_input()
    else:
        gRunManager.BeamOn(args.events)


    myEA.Shutdown()

