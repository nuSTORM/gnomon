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
from gnomon.DetectorConstruction import VlenfDetectorConstruction
from gnomon import Logging

log = None  #  Logger for this file

def check_valid_energy_arg(input_var):
    """ Check that it's either an int, float, or 'e' or 'mu'"""
    if input_var == 'electron' or input_var == 'e':
        return 'e'
    elif input_var == 'muon' or input_var =='m':
        return 'm'
    else:
        try:
            return float(input_var)
        except:
            pass

    msg = "%r is neither a number nor the string 'electron' or 'muon'" % input_var
    raise argparse.ArgumentTypeError(msg)

def is_neutrino_code(pdg_code):
    if math.fabs(pdg_code) in [12,14,16]:
        return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate the NuSTORM experiment magnetized iron detectors')

    Logging.addLogLevelOptionToArgs(parser)  #  adds --log_level

    Configuration.PopulateArgs(parser)
    #parser.add_argument('--name', '-n', help='DB in CouchDB for output',
    #                    type=str, required=True)
    #parser.add_argument('--events', help='how many events to simulate',
    #                    type=int, default=10)
    #parser.add_argument('--run', help='run number (random if 0)',
    #                    type=int, default=0)
    #parser.add_argument('--seed', help='random seed, 0 means set to clock',
    #                    type=int, default=0)
    #parser.add_argument('--polarity', choices=['+','-','0'], default='+', help='field polarity')

    group = parser.add_argument_group('GeneratorAction', 'Specify the particles to simulate')
    #group.add_argument('--energy', type=check_valid_energy_arg, help="Either a number for a fixed energy (MeV), or 'electron' or 'muon' for energies following their respective neutrino energy distributions", required=True)
    #group.add_argument('--pid', type=int, help='Geant4 particle number.  If neutrino, use Genie for the particle interaction.', required=True)

    group2 = group.add_mutually_exclusive_group(required=True)
    group2.add_argument('--vertex', metavar='N', type=float, nargs=3, help='Vertex location (mm)')
    group2.add_argument('--uniform', '-u', action='store_true', help='Vertex uniformly distributed')

    args = parser.parse_args()

    Logging.setupLogging(args.log_level, args.name)
    log = logging.getLogger('root').getChild('simulate')
    log.debug('Commandline args: %s', str(args))

    random.seed()

    config = Configuration.DEFAULT(args.name, args.run_number)
    Configuration.GLOBAL_CONFIG = config.getConfigurationDict()

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

    exN03PL = G4.G4physicslists.QGSP_BERT()
    gRunManager.SetUserInitialization(exN03PL)
    exN03PL.SetDefaultCutValue(1.0 * mm)
    exN03PL.SetCutsWithDefault()

    #
    #  Generator actions
    #


    if is_neutrino_code(args.pid):
        pga = GeneratorAction.GenieGeneratorAction(args.events, args.pid, args.energy)
    else:
        pga = GeneratorAction.SingleParticleGeneratorAction()
        pga.setTotalEnergy(args.energy)
        pga.setPID(args.pid)

    if args.vertex:
        pga.setVertex(args.vertex)
    elif args.uniform:
        pga.setVertex('uniform')


    gRunManager.SetUserAction(pga)

    myEA = EventAction.VlenfEventAction(pga)
    gRunManager.SetUserAction(myEA)

    gRunManager.Initialize()

    #  This is a trick that, if enabled, lets the event action notify the
    #  detector when the event is over.  This allows the sensitive detector
    #  to perform a bulk commit of 'mchit's to the event store.  It's meant
    #  to be an optimization since writing tons of small 'mchit's individually
    #  to the database is slow.
    sd = detector.getSensitiveDetector()
    myEA.setSD(sd)

    gRunManager.BeamOn(args.events)


    myEA.Shutdown()

