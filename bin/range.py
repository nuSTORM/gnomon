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
from gnomon.DetectorConstruction import BoxDetectorConstruction
from gnomon import Logging
from gnomon.SD import EmitNothingSD

from scipy.stats import uniform

log = None  # Logger for this file


def is_neutrino_code(pdg_code):
    if math.fabs(pdg_code) in [12, 14, 16]:
        return True
    return False

if __name__ == "__main__":
    #material = 'iron_scint_bars'
    material = sys.argv[1]

    name = 'range_test_%s' % material
    run = 0

    random.seed()

    config_class = Configuration.DEFAULT(name, run)
    Configuration.GLOBAL_CONFIG = config_class.get_configuration_dict()

    Logging.setupLogging('DEBUG', name)
    log = logging.getLogger('root').getChild('simulate')

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

    detector = BoxDetectorConstruction('%s.gdml' % material)
    gRunManager.SetUserInitialization(detector)

    physics_list = G4.G4physicslists.QGSP_BERT()
    gRunManager.SetUserInitialization(physics_list)
    physics_list.SetDefaultCutValue(1.0 * mm)
    physics_list.SetCutsWithDefault()

    pos = []
    pos.append(uniform(loc=-1000, scale=2000))
    pos.append(uniform(loc=-1000, scale=2000))
    pos.append(uniform(loc=-1000, scale=2000))
    mom = [0,0, uniform(loc=0, scale=10000)] # MeV
    pid = 13

    pga = GeneratorAction.ParticleGenerator(pos, mom, pid)
    pga = GeneratorAction.VlenfGeneratorAction(pga)

    gRunManager.SetUserAction(pga)

    processors = []
    processors.append("AppendTruth")
    processors.append("CouchManager")

    myEA = EventAction.VlenfEventAction(processors)
    gRunManager.SetUserAction(myEA)

    myTA = TrackingAction.LengthTrackingAction()
    gRunManager.SetUserAction(myTA)


    #  This is a trick that, if enabled, lets the event action notify the
    #  detector when the event is over.  This allows the sensitive detector
    #  to perform a bulk commit of 'mchit's to the event store.  It's meant
    #  to be an optimization since writing tons of small 'mchit's individually
    #  to the database is slow.
    sd = EmitNothingSD()
    myEA.setSD(sd)

    gRunManager.Initialize()

    gRunManager.BeamOn(int(1e6))

    myEA.shutdown()
