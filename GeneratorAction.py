"""Generator actions

These classes are used to tell Geant4 what particles it is meant to simulate.
One always has to inherit from a UserPrimaryGeneratorAction base class in Geant4
and then define the function GeneratePrimaries.
"""

import Geant4 as G4
import ROOT

import logging
import sys
import os
import random
import tempfile

class VlenfGeneratorAction(G4.G4VUserPrimaryGeneratorAction):
    """Base class for VLENF generator actions"""
    def __init__(self):
        G4.G4VUserPrimaryGeneratorAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.vertex = (0, 0, 0)  #  mm
        self.log.debug('Default vertex: %s', str(self.vertex))

    def check3Vector(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong type for 3-vector')
        if len(value) != 3:
            raise ValueError('Wrong dimensions for 3-vector')
        for element in value:
            if not isinstance(element, (float, int)):
                raise ValueError('3-vector element is not number')

    def SetPosition(self, v):
        if self.vertex == 'uniform':
            x = random.uniform(-2500, 5000)
            y = random.uniform(-2500, 5000)
            z = random.uniform(-30*222, 30*222)
            self.log.debug('Using vertex %f %f %f', x, y, z)
            v.SetPosition(x,y,z)
        else:
            v.SetPosition(self.vertex[0] * G4.mm,
                          self.vertex[1] * G4.mm,
                          self.vertex[2] * G4.mm)

    def setVertex(self, vertex):
        if vertex == 'uniform':
            self.log.info('Using uniform vertex')
            self.vertex = 'uniform'
        else:
            self.check3Vector(vertex)
            
            self.log.info('Vertex set to (mm): %s', str(vertex))
            self.vertex = vertex
        

class SingleParticleGeneratorAction(VlenfGeneratorAction):
    """Generate single particle at specific point"""
    def __init__(self):
        VlenfGeneratorAction.__init__(self)
        
        self.momentum = (0, 0, 1) # MeV/c
        self.pid = -13

    def setMomentum(self, momentum):
        self.check3Vector(momentum)

        self.log.info('Momentum set to (MeV): %s', str(momentum))
        self.momentum = momentum

    def setPID(self, pid):
        if not isinstance(pid, int):
            raise ValueError('PID must be integer')
        self.pid = pid
        
    def GeneratePrimaries(self, event):
        pp = G4.G4PrimaryParticle()
        pp.SetPDGcode(self.pid)

        pp.SetMomentum(self.momentum[0],
                       self.momentum[1],
                       self.momentum[2]) # MeV/c

        v = G4.G4PrimaryVertex()
        self.SetPosition(v)
        v.SetPrimary(pp)

        event.AddPrimaryVertex(v)
    
class GenieGeneratorAction(VlenfGeneratorAction):
    """Generate events from a Genie ntuple"""

    def __init__(self, event_type, nevents):
        VlenfGeneratorAction.__init__(self)
        self.event_list = self.get_next_events()

        self.event_type = event_type
        self.nevents = nevents

        self.generate_file()

        self.mc_info = None  # Info on what is simulated

    def getMCInfo(self):
        return self.mc_info

    def generate_file(self):
        id, filename = tempfile.mkstemp(suffix='.root')

        #export GSPLOAD=$DATA_DIR/xsec.xml

        fake_run = random.randint(1, sys.maxint) # avoids race conditions

        if self.event_type == 'mu_bar_bkg':
            os.system("GSPLOAD=data/xsec.xml gevgen -p -14 -r %d -t 1000260560 -n %d -e 0.1,2.0 -f data/flux_file_mu.dat  > /dev/null" % (fake_run, self.nevents))
        elif self.event_type == 'mu_sig'
            os.system("GSPLOAD=data/xsec.xml gevgen -p 14 -r %d -t 1000260560 -n %d -e 0.1,2.0 -f data/flux_file_e.dat  > /dev/null" % (fake_run, self.nevents))
        else:
            raise ValueError()
        os.system("gntpc -i gntp.%d.ghep.root -o %s -f gst > /dev/null" % (fake_run, filename))
        os.system('rm gntp.%d.ghep.root' % fake_run)
        self.filename = filename
        

    def get_next_events(self):
        f = ROOT.TFile(self.filename)
        try:
            t = f.Get('gst')
            n = t.GetEntries()
        except:
            self.log.critical('Could not open the ROOT file with Genie events')
            raise

        for i in range(n):
            t.GetEntry(i)
            next_events = []

            lepton_event = {}
            if t.El ** 2 - (t.pxl ** 2 + t.pyl ** 2 + t.pzl ** 2) < 1e-7:
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

            event_type = {}

            self.log.debug('Event type:')
            for my_type in ['qel', 'res', 'dis', 'coh', 'dfr',
                         'imd', 'nuel', 'em']:
                self.log.debug('\t%s:%d', my_type, t.__getattr__(my_type))
                event_type[my_type] = t.__getattr__(my_type)

            self.log.debug('Propogator:')
            for prop in ['nc', 'cc']:
                self.log.debug('\t%s:%d', prop, t.__getattr__(prop))
                event_type[prop] = t.__getattr__(prop)

            self.log.debug('y: %f', t.y)
            try:
                self.log.debug('m_l: %f', math.sqrt(t.El ** 2 -
                                        (t.pxl ** 2 + t.pyl ** 2 + t.pzl ** 2)))
            except:
                pass

            yield next_events, event_type

    def GeneratePrimaries(self, event):
        particles, event_type = next(self.event_list)

        self.mc_info = {'particles' : particles, 'event_type' : event_type}

        for particle in particles:
            pp = G4.G4PrimaryParticle()
            pp.SetPDGcode(particle['code'])

            particle['px'], particle['py'], particle['pz'] = \
                [1000 * x for x in [particle['px'], particle['py'],
                                    particle['pz']]]  # GeV -> MeV

            pp.SetMomentum(particle['px'], particle['py'], particle['pz'])

            v = G4.G4PrimaryVertex()
            self.SetPosition(v)
            v.SetPrimary(pp)

            event.AddPrimaryVertex(v)
