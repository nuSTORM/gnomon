import sys
from time import sleep

from Geant4 import HepRandom, gRunManager, gTransportationManager, gApplyUICommand

from Tkinter import Frame, Label, IntVar, Scale, Button, W, Checkbutton
from Tkinter import DoubleVar, HORIZONTAL, StringVar, Entry, E

class VlenfApp(Frame):
    g4pipe = 0

    def init(self):
        title = Label(self, text="VLENFsim")
        title.grid(row=0, column=1, columnspan=3)
        header = Label(self, text="empowered by \n Geant4Py")
        header.grid(row=1, column=1, columnspan=3)

        eventLabel = Label(self, bg="green",  text="Events")
        self.eventVar = IntVar()
        self.eventVar.set(1)
        event = Scale(self, orient=HORIZONTAL, length=400, from_=0, to=10**4, tickinterval=10**4, resolution=1, variable=self.eventVar)
        eventLabel.grid(row=10, column=0, sticky=W)
        event.grid(row=10, column=1, columnspan=5, sticky=W)

        startBut = Button(self, bg="orange", text="Start a run", command=self.cmd_beamOn)
        startBut.grid(row=0, column=0, sticky=W)

        processLabel = Label(self, text="Process on/off", bg="green")
        processLabel.grid(row=11, column=0, sticky=W)
        procTab = {}

        self.processList = ["phot", "compt", "conv", "msc", "eIoni", "eBrem", "annihil", "muIoni", "muBrems", "hIoni"]
        pos = 1
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
            pos = pos+1
            procTab[i].select()

        
        cutLabel = Label(self, bg="green",  text="Cut (mm)")

        self.cutVar = DoubleVar()
        self.cutVar.set(1.)
        cut = Scale(self, orient=HORIZONTAL, length=400, from_=0., to=10., tickinterval=5., resolution=0.005, variable=self.cutVar, digits=5)
        cutLabel.grid(row=14, column=0, sticky=W)
        cut.grid(row=14, column=1, columnspan=5, sticky=W)

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

        g4comLabel = Label(self, text="Geant4 command", bg="orange")
        self.g4commandVar = StringVar()
        commandEntry = Entry(self, textvariable=self.g4commandVar, width=15)
        self.g4commandVar.set("/vis/viewer/zoom 1.2")
        comBut = Button(self, bg="orange", text="Execute", command=self.cmd_g4command)
        g4comLabel.grid(row=17, column=0, sticky=W)
        commandEntry.grid(row=17, column=1, columnspan=3, sticky=E+W)
        comBut.grid(row=17, column=5)
        
        exitBut = Button(self, bg="red", text="End all", command=sys.exit)
        exitBut.grid(row=0, column=5, sticky=W)


    def cmd_beamOn(self):
        position = 0

        print "Now geometry updated"

        eventNum = self.eventVar.get()
        for i in range(eventNum):
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
