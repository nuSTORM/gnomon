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

    detector = BoxDetectorConstruction('%s.gdml' % material)
    gRunManager.SetUserInitialization(detector)

    physics_list = G4.G4physicslists.QGSP_BERT()
    gRunManager.SetUserInitialization(physics_list)
    physics_list.SetDefaultCutValue(1.0 * mm)
    physics_list.SetCutsWithDefault()



    #  These kinetic energies come from the range tables found at:
    #
    # http://pdg.lbl.gov/2008/AtomicNuclearProperties/
    # 
    kinetic_energies = [1.0, 1.2, 1.4, 1.7, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0, 17.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 70.0, 80.0, 90.0, 100.0, 120.0, 140.0, 170.0, 200.0, 250.0, 273.6, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1200.0, 1400.0, 1700.0, 2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4500.0, 5000.0] # MeV
    muon_mass = 105.65836668 # MeV, TODO FIXME, don't hard code!

    pga_list = []
    for kinetic_energy in kinetic_energies:
        pga = GeneratorAction.ParticleGenerator()
        pga.set_momentum([0,0,kinetic_energy + muon_mass])
        pga.set_pid(13) # muon

        
        pga.set_position([0,0,0]) 
        pga_list.append(pga)


    pga = GeneratorAction.VlenfGeneratorAction(pga)
    #gpga = GeneratorAction.GroupGeneratorAction(pga_list) 

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
