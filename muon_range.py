#!/usr/bin/env python
#from Geant4 import *
import Geant4 as G4
from Geant4 import HepRandom, gRunManager, gTransportationManager, gApplyUICommand
from Geant4 import mm
import g4py.ExN03geom
import g4py.ExN03pl
import g4py.ParticleGun
import sys
import math

import argparse

import EventAction
import SD
import ToroidField
from GenieGeneratorAction import GenieGeneratorAction
from GUI import VlenfApp

rand_engine = G4.Ranlux64Engine()
HepRandom.setTheEngine(rand_engine)
HepRandom.setTheSeed(20050830)


class MyDetectorConstruction(G4.G4VUserDetectorConstruction):
    "My Detector Construction"

    def __init__(self):
        G4.G4VUserDetectorConstruction.__init__(self)
        self.world = None
        self.gdml_parser = G4.G4GDMLParser()
        self.sd = None

    def __del__(self):
        pass

    def getSD(self):
        return self.sd

    def Construct(self):
        filename = "gdml/iron_scint_bars.gdml"
        self.gdml_parser.Read(filename)
        self.world = self.gdml_parser.GetWorldVolume()

        for i in range(6):
            print i, G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(i).GetName()

        layers = self.gdml_parser.GetConstant("layers")
        bars = self.gdml_parser.GetConstant("bars")
        width = self.gdml_parser.GetConstant("width")
        thickness_layer = self.gdml_parser.GetConstant("thickness_layer")
        thickness_bar = self.gdml_parser.GetConstant("thickness_bar")

        self.sd = SD.ScintSD(layers, bars, width, thickness_layer, thickness_bar)

        #lv = G4LogicalVolumeStore.GetInstance().GetVolume("ScintillatorPlane",True)
        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(1)
        assert lv.GetName() == "ScintillatorBarX"
        print 'using sd as %s' % lv.GetName()
        lv.SetSensitiveDetector(self.sd)

        lv = G4.G4LogicalVolumeStore.GetInstance().GetVolumeID(2)
        assert lv.GetName() == "ScintillatorBarY"
        lv.SetSensitiveDetector(self.sd)

        return self.world

exN03geom = MyDetectorConstruction()
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

#gRunManager.BeamOn(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate the VLENF')
    parser.add_argument('--number_events', help='how many events to simulate', type=int, default=1)

    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--event_display', action='store_true')
    parser.add_argument('--view', choices=['XY', 'ZY', 'ZX'], default='ZX')

    parser.add_argument('--pause', help='pause after each event, require return')
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
