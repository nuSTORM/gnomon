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

# gnomon
from gnomon import Configuration
from gnomon import EventAction
from gnomon import GeneratorAction
from gnomon import TrackingAction
from gnomon.DetectorConstruction import MagIronSamplingCaloDetectorConstruction
from gnomon.Configuration import RUNTIME_CONFIG as rc
from gnomon import Logging

from scipy.stats import uniform

log = None  # Logger for this file

if __name__ == "__main__":
    desc = 'Simulate the NuSTORM experiment magnetized iron detectors'
    parser = argparse.ArgumentParser(description=desc)

    Logging.addLogLevelOptionToArgs(parser)  # adds --log_level

    Configuration.populate_args(parser)
    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
        type=str, required=True)
    parser.add_argument('--run', '-r', help='run number',
        type=int, required=True)

    args = parser.parse_args()

    config_class = Configuration.DEFAULT(args.name, args.run,
        overload=vars(args))
    Configuration.GLOBAL_CONFIG = config_class.get_configuration_dict()

    Logging.setupLogging(args.log_level, args.name)
    log = logging.getLogger('root').getChild('simulate')
    log.debug('Commandline args: %s', str(args))

    random.seed()

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

    detector = MagIronSamplingCaloDetectorConstruction(field_polarity=config['polarity'])
    gRunManager.SetUserInitialization(detector)

    physics_list = G4.G4physicslists.QGSP_BERT()
    gRunManager.SetUserInitialization(physics_list)
    physics_list.SetDefaultCutValue(1.0 * mm)
    physics_list.SetCutsWithDefault()

    #
    #  Generator actions
    #

    pos = []
    width = rc['width'] * rc['bars']

    pos.append(uniform(loc=-width / 2, scale=width))
    pos.append(uniform(loc=-width / 2, scale=width))
    pos.append(GeneratorAction.composite_z(rc))

    #config['vertex']
    mom = [0, 0, config['energy_MeV']]
    pid = config['pid']

    if GeneratorAction.is_neutrino_code(config['pid']):
        if config['distribution'] == 'point':
            raise NotImplementedError

        assert config['distribution'] == 'electron' or\
               config['distribution'] == 'muon' or\
               config['distribution'] == 'flat'

        log.warning('Energy argument ignored... assuming 3.8 GeV muons')

        pga = GeneratorAction.GenieGenerator(pos, mom, pid)

    else:
        if config['distribution'] != 'point':
            raise NotImplementedError
        pga = GeneratorAction.ParticleGenerator(pos, mom, pid)

    pga = GeneratorAction.VlenfGeneratorAction(pga)
    gRunManager.SetUserAction(pga)

    processors = []
    processors.append("VlenfSimpleDigitizer")
    processors.append("EmptyTrackFromDigits")
    processors.append("FiducialCuts")
    processors.append("ExtractTracks")
    processors.append("CombineViews")
    processors.append("VlenfPolynomialFitter")
    processors.append("ClassifyVariables")
    processors.append("AppendTruth")
    processors.append("AppearanceCuts")
    processors.append("SaveInteresting")
    processors.append("CouchManager")

    myEA = EventAction.VlenfEventAction(processors)
    gRunManager.SetUserAction(myEA)

    myTA = TrackingAction.LengthTrackingAction()
    gRunManager.SetUserAction(myTA)

    gRunManager.Initialize()

    #  This is a trick that, if enabled, lets the event action notify the
    #  detector when the event is over.  This allows the sensitive detector
    #  to perform a bulk commit of 'mchit's to the event store.  It's meant
    #  to be an optimization since writing tons of small 'mchit's individually
    #  to the database is slow.
    sd = detector.get_sensitive_detector()
    myEA.setSD(sd)

    gRunManager.BeamOn(config['events'])

    myEA.shutdown()
