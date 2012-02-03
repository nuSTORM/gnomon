#!/usr/bin/env python
from Geant4 import *
import g4py.ExN03geom
import g4py.ExN03pl
import g4py.ParticleGun
import sys
from time import sleep
#from subprocess import *
import ROOT
import math

rand_engine= Ranlux64Engine()
HepRandom.setTheEngine(rand_engine)
HepRandom.setTheSeed(20050830L)

import my_script

class MyTrackingAction(G4UserTrackingAction):
  "My tracking Action"

  def PreUserTrackingAction(self, track):
    pass
  
  def PostUserTrackingAction(self, track):
    pass
    

class MyPrimaryGeneratorAction(G4VUserPrimaryGeneratorAction):
  "My Primary Generator Action"

  def __init__(self):
    G4VUserPrimaryGeneratorAction.__init__(self)
    self.event_list = self.get_next_events()

  def get_next_events(self):
    f = ROOT.TFile('ntuple_neg14.root')
    t = f.Get('gst')

    n = t.GetEntries()

    for i in range(n):
      t.GetEntry(i)
      next_events = []

      lepton_event = {}
      if t.El**2 - (t.pxl**2 + t.pyl**2 + t.pzl**2) < 1e-7:
        lepton_event['code'] = -14
      else:
        lepton_event['code'] = -13
      lepton_event['E'] = t.El
      lepton_event['px'] = t.pxl
      lepton_event['py'] = t.pyl
      lepton_event['pz'] = t.pzl

      next_events.append(lepton_event)


      for j in range(t.nf):  # nf, number final hadronic states                 
        hadron_event = {}
        hadron_event['code'] = t.pdgf[j]
        hadron_event['E'] = t.Ef[j]
        
        hadron_event['px'] = t.pxf[j]
        hadron_event['py'] = t.pyf[j] 
        hadron_event['pz'] = t.pzf[j] 

        next_events.append(hadron_event)


      print 'nc', t.__getattr__('nc')
      print 'Event type:'
      for type in ['qel', 'res', 'dis', 'coh', 'dfr', 'imd', 'nuel', 'em']:
        print '\t', type, ':', t.__getattr__(type)

      print 'Propogator:'
      for prop in ['nc', 'cc']:
        print '\t', prop, ':', t.__getattr__(prop)


      print 'y:', t.y
      try:
        print 'm_l:', math.sqrt(t.El**2 - (t.pxl**2 + t.pyl**2 + t.pzl**2))
      except:
        pass
      print lepton_event

      yield next_events

  def GeneratePrimaries(self, event):
    events = self.event_list.next()
    for particle in events:
      pp = G4PrimaryParticle()
      pp.SetPDGcode(particle['code'])
      
      particle['px'], particle['py'], particle['pz'] = [1000*x for x in [particle['px'], particle['py'], particle['pz']]]  # GeV -> MeV

      temp = particle['pz']
      particle['pz'] = particle['px']
      particle['px'] = temp

      pp.SetMomentum(particle['px'], particle['py'], particle['pz'])
      
      v = G4PrimaryVertex()
      v.SetPosition(0.0, 0.0, 0.0)
      v.SetPrimary(pp)
      
      event.AddPrimaryVertex(v)

exN03geom= g4py.ExN03geom.ExN03DetectorConstruction()
gRunManager.SetUserInitialization(exN03geom)

exN03PL= g4py.ExN03pl.PhysicsList()
gRunManager.SetUserInitialization(exN03PL)

myEA= MyTrackingAction()
gRunManager.SetUserAction(myEA)

pgPGA= MyPrimaryGeneratorAction()
gRunManager.SetUserAction(pgPGA)

gRunManager.Initialize()

# visualization
gApplyUICommand("/vis/sceneHandler/create OGLSX OGLSX")
gApplyUICommand("/vis/viewer/create OGLSX oglsxviewer")
gApplyUICommand("/vis/drawVolume")
gApplyUICommand("/vis/scene/add/trajectories")
gApplyUICommand("/tracking/storeTrajectory 1")
gApplyUICommand("/vis/scene/endOfEventAction accumulate")
gApplyUICommand("/vis/scene/endOfRunAction accumulate")
gApplyUICommand("/vis/viewer/select  oglsxviewer")


# creating widgets using grid layout

from Tkinter import *

class App(Frame):

  g4pipe = 0

  def init(self):

#title and header    row=0, 1
    title = Label(self, text="VLENFsim")
    title.grid(row=0, column=1, columnspan=3)
    header = Label(self, text="empowered by \n Geant4Py")
    header.grid(row=1, column=1, columnspan=3)
# number of layers
    layerLabel = Label(self, bg="green",  text="No of layers")
    self.layerVar=IntVar()
    self.layerVar.set(50)
    layer = Scale(self,  orient=HORIZONTAL, length=400, from_=0, to=300, tickinterval=100, resolution=1, variable=self.layerVar )
    layerLabel.grid(row=2, column=0, sticky=W)
    layer.grid(row=2, column=1, columnspan=5, sticky=W)

#absorber thickness row=4
    absorberthickLabel = Label(self, bg="green", text="Thickness (mm)")
    self.absorberthickVar = DoubleVar()
    self.absorberthickVar.set(10.0)
    absorberthick = Scale(self, orient=HORIZONTAL, length=400, from_=0., to=100., resolution=0.05, tickinterval=10.0, digits=4, variable=self.absorberthickVar)
    absorberthickLabel.grid(row=4, column=0, sticky=W)
    absorberthick.grid(row=4, column=1, columnspan=5, sticky=W)


#gap material selection row=5
    self.gapmaterialVar = StringVar()
    self.gapmaterialVar.set("Scintillator")


#gap thickness row=6
    gapthickLabel = Label(self, bg="green", text="Thickness (mm)")
    self.gapthickVar = DoubleVar()
    self.gapthickVar.set(10.0)
    gapthick = Scale(self, orient=HORIZONTAL, length=400, from_=0., to=100., resolution=0.05, tickinterval=10.0, digits=4, variable=self.gapthickVar)
    gapthickLabel.grid(row=6, column=0, sticky=W)
    gapthick.grid(row=6, column=1, columnspan=5, sticky=W)

#calorSizeYZ row=7
    calorsizeYZLabel = Label(self, bg="green", text="SizeYZ (mm)")
    self.calorsizeYZVar = DoubleVar()
    self.calorsizeYZVar.set(1000.0)
    calorsizeYZ = Scale(self, orient=HORIZONTAL, length=400, from_=0., to=5000., resolution=0.05, tickinterval=1000.0, digits=4, variable=self.calorsizeYZVar)
    calorsizeYZLabel.grid(row=7, column=0, sticky=W)
    calorsizeYZ.grid(row=7, column=1, columnspan=5, sticky=W)

#number of event row=10
    eventLabel = Label(self, bg="green",  text="Events")
    self.eventVar=IntVar()
    self.eventVar.set(1)
    event = Scale(self,  orient=HORIZONTAL, length=400, from_=0, to=10**4, tickinterval=10**4, resolution=1, variable=self.eventVar )
    eventLabel.grid(row=10, column=0, sticky=W)
    event.grid(row=10, column=1, columnspan=5, sticky=W)

#start a run button row=0
    startBut = Button(self, bg="orange", text="Start a run", command=self.cmd_beamOn)
    startBut.grid(row=0, column=0, sticky=W)

# process activate row 11 - 13
    processLabel=Label(self, text="Process on/off", bg="green")
    processLabel.grid(row=11, column=0, sticky=W)
    procTab = {}

    self.processList = ["phot", "compt", "conv", "msc", "eIoni", "eBrem", "annihil","muIoni", "muBrems", "hIoni"]
    pos=1
    self.processVar = {}
    for i in self.processList:
      self.processVar[i] = IntVar()
      procTab[i] = Checkbutton(self, text=i, variable=self.processVar[i], command=self.cmd_setProcess)
      if pos <= 3:
        procTab[i].grid(row=11, column=pos, sticky=W)
      if 4<= pos <= 7:
        procTab[i].grid(row=12, column=pos-3, sticky=W)
      if pos >= 8:
        procTab[i].grid(row=13, column=pos-7, sticky=W)
      pos=pos+1
      procTab[i].select()
# set cuts row 14
    cutLabel = Label(self, bg="green",  text="Cut (mm)")

    self.cutVar=DoubleVar()
    self.cutVar.set(1.)
    cut = Scale(self, orient=HORIZONTAL, length=400, from_=0., to=10., tickinterval=5., resolution=0.005, variable=self.cutVar, digits=5 )
    cutLabel.grid(row=14, column=0, sticky=W)
    cut.grid(row=14, column=1, columnspan=5, sticky=W)

# set mag field row 15
    magLabel = Label(self, bg="green",  text="Magnetic (T)")

    self.magVar=DoubleVar()
    self.magVar.set(2.)
    mag = Scale(self, orient=HORIZONTAL, length=400, from_=0., to=5., tickinterval=1., resolution=0.1, variable=self.magVar, digits=3 )
    magLabel.grid(row=15, column=0, sticky=W)
    mag.grid(row=15, column=1, columnspan=5, sticky=W)

#Geant4 command entry row = 17
    g4comLabel = Label(self, text="Geant4 command", bg="orange")
    self.g4commandVar = StringVar()
    commandEntry = Entry(self, textvariable=self.g4commandVar, width=15)
    self.g4commandVar.set("/vis/viewer/zoom 1.2")
    comBut = Button(self, bg="orange", text="Execute", command=self.cmd_g4command)
    g4comLabel.grid(row=17, column=0, sticky=W)
    commandEntry.grid(row=17, column=1, columnspan=3, sticky=E+W)
    comBut.grid(row=17, column=5)

#exit row = 0
    exitBut = Button(self, bg="red", text="End all", command=sys.exit)
    exitBut.grid(row=0, column=5, sticky=W)

#on Run butto do...
  def cmd_beamOn(self):
      exN03geom.SetNbOfLayers(self.layerVar.get())
      exN03geom.SetAbsorberMaterial("Iron")
      exN03geom.SetAbsorberThickness(self.absorberthickVar.get()  * mm/2.0)
      exN03geom.SetGapMaterial(self.gapmaterialVar.get())
      exN03geom.SetGapThickness(self.gapthickVar.get()  * mm/2.0)
      exN03geom.SetCalorSizeYZ(self.calorsizeYZVar.get() * mm)
      position =  -self.layerVar.get()*(self.absorberthickVar.get() + self.gapthickVar.get()) * mm / 4
      position = 0

      exN03geom.UpdateGeometry()
      exN03PL.SetDefaultCutValue(self.cutVar.get() * mm)
      exN03PL.SetCutsWithDefault()
      exN03geom.SetMagField(self.magVar.get() * tesla)

      print "Now geometry updated"


      eventNum = self.eventVar.get()
      for i in range(eventNum):

        #pg.SetParticlePosition(G4ThreeVector(position*mm, 0.*mm, 0.*cm))
        gRunManager.BeamOn(1)
        gApplyUICommand("/vis/viewer/flush")
        sleep(0.01)
      gApplyUICommand("/vis/viewer/update")

  def cmd_setProcess(self):
    for i in self.processList:
      if self.processVar[i].get() == 0:
         gProcessTable.SetProcessActivation(i, 0)
         print "Process " + i + " inactivated"
      else:
         gProcessTable.SetProcessActivation(i, 1)
         print "Process " + i + " activated"

  def cmd_g4command(self):
    gApplyUICommand(self.g4commandVar.get())


  def cmd_viewer(self):
    gApplyUICommand("/vis/viewer/select oglsxviewer")
    gApplyUICommand("/vis/scene/add/trajectories")
    
    gApplyUICommand("/tracking/storeTrajectory 1")
    gApplyUICommand("/vis/scene/endOfEventAction accumulate")
    gApplyUICommand("/vis/scene/endOfRunAction accumulate")
    

  def cmd_expand(self):
    gApplyUICommand("/vis/viewer/zoom 1.2")

  def cmd_pan(self):
    gApplyUICommand("/vis/viewer/pan " + self.panXYVar.get() + " "  + " mm")


  def cmd_shrink(self):
    gApplyUICommand("/vis/viewer/zoom 0.8")



  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.init()
    self.grid()


app = App()
app.mainloop()
