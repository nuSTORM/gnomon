#!/usr/bin/env python

# system libraries
import sys
import argparse
import logging
import os
import math
import random

# Geant4
temp = sys.stdout  # backup stdout
sys.stdout = open(os.devnull)  # make fake stdout
import Geant4 as G4  # Then silently import Geant4!
from Geant4 import HepRandom, gRunManager
from Geant4 import gTransportationManager, gApplyUICommand, mm
sys.stdout = temp  # Then return sys.stdout

# gnomon
from gnomon import Configuration
from gnomon import EventAction
from gnomon import GeneratorAction
from gnomon import TrackingAction
from gnomon.DetectorConstruction import IronBoxDetectorConstruction
from gnomon import Logging

log = None  # Logger for this file


def is_neutrino_code(pdg_code):
    if math.fabs(pdg_code) in [12, 14, 16]:
        return True
    return False

if __name__ == "__main__":
    name = 'range_test'
    run = 0

    Logging.setupLogging('DEBUG', name)
    log = logging.getLogger('root').getChild('simulate')

    random.seed()

    config_class = Configuration.DEFAULT(name, run)
    Configuration.GLOBAL_CONFIG = config_class.get_configuration_dict()

    # make shorter variable name for us
    config = config_class.get_configuration_dict()

    log.info('Using the following configuration:')
    log.info(config)

    rand_engine = G4.Ranlux64Engine()
    HepRandom.setTheEngine(rand_engine)
    seed = config['seed']
    if seed == 0:
        seed = random.randint(1, 65536)
        log.warning('Using random seed %d', seed)
    else:
        log.info('Using seed %d', seed)
    HepRandom.setTheSeed(seed)

    detector = IronBoxDetectorConstruction()
    gRunManager.SetUserInitialization(detector)

    physics_list = G4.G4physicslists.QGSP_BERT()
    gRunManager.SetUserInitialization(physics_list)
    physics_list.SetDefaultCutValue(1.0 * mm)
    physics_list.SetCutsWithDefault()

    #
    #  Generator actions
    #


    pga = GeneratorAction.SingleParticleGeneratorAction()
    pga.setTotalEnergy(2000) # MeV
    pga.setPID(13) # muon

    pga.setVertex([0,0,0])

    gRunManager.SetUserAction(pga)

    myEA = EventAction.VlenfEventAction(pga)
    gRunManager.SetUserAction(myEA)

    myTA = TrackingAction.LengthTrackingAction()
    gRunManager.SetUserAction(myTA)

    gRunManager.Initialize()

    gRunManager.BeamOn(config['events'])

    myEA.shutdown()
