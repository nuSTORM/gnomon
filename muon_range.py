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
HepRandom.setTheSeed(20050830)

class ScintSD(G4VSensitiveDetector):
  "SD for scint"

  def __init__(self):
    G4VSensitiveDetector.__init__(self, "Scintillator")

  def ProcessHits(self, step, rohist):
    preStepPoint= step.GetPreStepPoint()
    if(preStepPoint.GetCharge() == 0):
      return

    #print 'test:', rohist.GetTranslation()

    track= step.GetTrack()

    pv = preStepPoint.GetPhysicalVolume()
    dedx= step.GetTotalEnergyDeposit()
    print('copy:',pv.GetCopyNo())
    print('\tobjectTranslation:', pv.GetObjectTranslation())
    print('\ttranslation:', pv.GetTranslation())
    print('\tframeTranslation:', pv.GetFrameTranslation())
    print('\tposition:', preStepPoint.GetPosition())
    print('\tdedx:', dedx)

    lv = pv.GetMotherLogical()
    print(lv.GetName())

    print('\trotation:', pv.GetRotation())
    print('\tobjectRotationValue:', pv.GetObjectRotationValue())
    print('\tframeRotation:', pv.GetFrameRotation())

class MyField(G4MagneticField):
  "My Magnetic Field"

  def GetFieldValue(self, pos, time):
    #current = 150 * 1000#  A
    #mu0 = 4 * math.pi * 10**-7
    r = math.sqrt( (pos.x)**2 + (pos.y )**2)

    bfield= G4ThreeVector()

    B = -2  * tesla # saturation
    if r != 0.0:
      #B += mu0 * current / (2 * math.pi * r * m) * tesla
      bfield.x= (pos.y / r) * B
      bfield.y= (pos.x / r) * B
    else:
      bfield.x= 0
      bfield.y= 0
    
    bfield.z= 0.

    #print pos, bfield
      
    return bfield

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


      print('nc', t.__getattr__('nc'))
      print('Event type:')
      for type in ['qel', 'res', 'dis', 'coh', 'dfr', 'imd', 'nuel', 'em']:
        print('\t', type, ':', t.__getattr__(type))

      print('Propogator:')
      for prop in ['nc', 'cc']:
        print('\t', prop, ':', t.__getattr__(prop))


      print('y:', t.y)
      try:
        print('m_l:', math.sqrt(t.El**2 - (t.pxl**2 + t.pyl**2 + t.pzl**2)))
      except:
        pass
      print(lepton_event)

      yield next_events

  def GeneratePrimaries(self, event):
    events = next(self.event_list)
    for particle in events:
      pp = G4PrimaryParticle()
      pp.SetPDGcode(particle['code'])
      
      particle['px'], particle['py'], particle['pz'] = [1000*x for x in [particle['px'], particle['py'], particle['pz']]]  # GeV -> MeV

      pp.SetMomentum(particle['px'], particle['py'], particle['pz'])
      
      v = G4PrimaryVertex()
      v.SetPosition(20.0, 20.0, 0.0)
      v.SetPrimary(pp)
      
      event.AddPrimaryVertex(v)

class MyDetectorConstruction(G4VUserDetectorConstruction):
  "My Detector Construction"

  def __init__(self):
    G4VUserDetectorConstruction.__init__(self)
    self.world= None
    self.gdml_parser= G4GDMLParser()

  def __del__(self):
    pass

  def Construct(self):
    filename = "gdml/iron_scint_bars.gdml"
    self.gdml_parser.Read(filename)
    self.world= self.gdml_parser.GetWorldVolume()
    

    for i in range(6):
      print(i, G4LogicalVolumeStore.GetInstance().GetVolumeID(i).GetName())
    self.x = ScintSD()
    #lv = G4LogicalVolumeStore.GetInstance().GetVolume("ScintillatorPlane",True)
    lv = G4LogicalVolumeStore.GetInstance().GetVolumeID(1)
    print('using sd as %s' % lv.GetName())
    lv.SetSensitiveDetector(self.x)
    
    return self.world

#exN03geom_dead= g4py.ExN03geom.ExN03DetectorConstruction()
exN03geom = MyDetectorConstruction()
gRunManager.SetUserInitialization(exN03geom)

exN03PL= g4py.ExN03pl.PhysicsList()
gRunManager.SetUserInitialization(exN03PL)

myEA= MyTrackingAction()
gRunManager.SetUserAction(myEA)

pgPGA= MyPrimaryGeneratorAction()
gRunManager.SetUserAction(pgPGA)

fieldMgr= gTransportationManager.GetFieldManager()

#print "uniform"
#myField= G4UniformMagField(G4ThreeVector(0.,2.*tesla,0.))
print("toroid")
myField= MyField()                                                             
fieldMgr.SetDetectorField(myField)
fieldMgr.CreateChordFinder(myField)

gRunManager.Initialize()

# visualization
gApplyUICommand("/vis/sceneHandler/create OGLSX OGLSX")
gApplyUICommand("/vis/viewer/create OGLSX oglsxviewer")
gApplyUICommand("/vis/drawVolume")
gApplyUICommand("/vis/scene/add/trajectories")
gApplyUICommand("/tracking/storeTrajectory 1")
gApplyUICommand("/vis/scene/endOfEventAction accumulate")
gApplyUICommand("/vis/scene/endOfRunAction accumulate")
gApplyUICommand("/vis/viewer/select oglsxviewer")

gApplyUICommand("/vis/scene/add/trajectories")

#gApplyUICommand("/vis/scene/endOfEventAction accumulate")
#gApplyUICommand("/vis/scene/endOfRunAction accumulate")

gRunManager.BeamOn(1000)

# creating widgets using grid layout

"""
from Tkinter import *

class App(Frame):

  g4pipe = 0

  def init(self):

#title and header    row=0, 1
    title = Label(self, text="VLENFsim")
    title.grid(row=0, column=1, columnspan=3)
    header = Label(self, text="empowered by \n Geant4Py")
    header.grid(row=1, column=1, columnspan=3)

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

    # set view, row 16
    setviewXYBut = Button(self, bg="red", text="X-Y", command=self.cmd_setviewXY)
    setviewXYBut.grid(row=16, column=2, sticky=W)

    setviewZYBut = Button(self, bg="red", text="Z-Y", command=self.cmd_setviewZY)
    setviewZYBut.grid(row=16, column=3, sticky=W)
    
    setviewZXBut = Button(self, bg="red", text="Z-X", command=self.cmd_setviewZX)
    setviewZXBut.grid(row=16, column=4, sticky=W)

    shrinkBut = Button(self, bg="red", text="shrink", command=self.cmd_shrink)
    shrinkBut.grid(row=16, column=0, sticky=W)

    expandBut = Button(self, bg="red", text="expand", command=self.cmd_expand)
    expandBut.grid(row=16, column=1, sticky=W)

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
      position = 0

      exN03PL.SetDefaultCutValue(self.cutVar.get() * mm)
      exN03PL.SetCutsWithDefault()
      #exN03geom_dead.SetMagField(self.magVar.get() * tesla)

      print("Now geometry updated")


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
         print("Process " + i + " inactivated")
      else:
         gProcessTable.SetProcessActivation(i, 1)
         print("Process " + i + " activated")

  def cmd_g4command(self):
    gApplyUICommand(self.g4commandVar.get())

  def cmd_setviewXY(self):
    gApplyUICommand("/vis/viewer/set/viewpointVector 0 0 -1")

  def cmd_setviewZY(self):
    gApplyUICommand("/vis/viewer/set/viewpointVector -1 0 0")

  def cmd_setviewZX(self):
    gApplyUICommand("/vis/viewer/set/viewpointVector -1 100000 0")

  def cmd_expand(self):
    gApplyUICommand("/vis/viewer/zoom 1.2")

  def cmd_shrink(self):
    gApplyUICommand("/vis/viewer/zoom 0.8")


  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.init()
    self.grid()


app = App()
app.mainloop()
"""
