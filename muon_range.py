#!/usr/bin/env python
#from Geant4 import *
import Geant4 as G4
from Geant4 import HepRandom, gRunManager
from Geant4 import gTransportationManager, gApplyUICommand
from Geant4 import mm
import g4py.ExN03geom
import g4py.ExN03pl
import g4py.ParticleGun

import argparse

import EventAction
import ToroidField
from GenieGeneratorAction import GenieGeneratorAction
from GUI import VlenfApp
from DetectorConstruction import VlenfDetectorConstruction

rand_engine = G4.Ranlux64Engine()
HepRandom.setTheEngine(rand_engine)
HepRandom.setTheSeed(20050830)

exN03geom = VlenfDetectorConstruction()
gRunManager.SetUserInitialization(exN03geom)

exN03PL = g4py.ExN03pl.PhysicsList()
gRunManager.SetUserInitialization(exN03PL)
exN03PL.SetDefaultCutValue(1.0 * mm)
exN03PL.SetCutsWithDefault()

myEA2 = EventAction.EventAction(exN03geom.getSD())
gRunManager.SetUserAction(myEA2)

pgPGA = GenieGeneratorAction()
gRunManager.SetUserAction(pgPGA)

fieldMgr = gTransportationManager.GetFieldManager()

myField = ToroidField.ToroidField()
fieldMgr.SetDetectorField(myField)
fieldMgr.CreateChordFinder(myField)

gRunManager.Initialize()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate the VLENF')
    parser.add_argument('--name', help='name for the simulation output')
    parser.add_argument('--number_events', help='how many events to simulate',
                        type=int, default=1)

    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--event_display', action='store_true')
    parser.add_argument('--view', choices=['XY', 'ZY', 'ZX'], default='ZX')

    parser.add_argument('--pause',
                        help='pause after each event, require return')
    args = parser.parse_args()

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
