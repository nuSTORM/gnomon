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
import math

def lookup_cc_partner(nu_pid):
    """Lookup the charge current partner

    Takes as an input neutrino nu_pid is a PDG code, then returns
    the charged lepton partner.  So 12 (nu_e) returns 11.  Keeps sign
    """

    neutrino_type = math.fabs(nu_pid)
    assert neutrino_type in [12, 14, 16]

    cc_partner = neutrino_type - 1  # get e, mu, tau
    cc_partner = math.copysign(cc_partner, nu_pid) # make sure matter/antimatter
    cc_partner = int(cc_partner)  # convert to int
    
    return cc_partner


class VlenfGeneratorAction(G4.G4VUserPrimaryGeneratorAction):
    """Base class for VLENF generator actions"""
    def __init__(self):
        G4.G4VUserPrimaryGeneratorAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.vertex = (0, 0, 0)  #  mm
        self.log.debug('Default vertex: %s', str(self.vertex))

        self.pid = 13 # PDG code

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
            x = random.uniform(-2500, 2500)
            y = random.uniform(-2500, 2500)
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
        
        self.beam_direction = G4.G4ThreeVector(0, 0, 1)

    def setTotalEnergy(self, energy):
        if not isinstance(energy, (int, float)):
            raise NotImplementedError("This function can only take numbers as the energy")

        self.log.info('Energy set to (MeV): %s', str(energy))
        self.energy = float(energy)

    def getMCInfo(self):
        info = {}
        info['particle_energy'] = self.energy
        info['pid'] = self.pid
        info['generator_action'] = 'SingleParticleGeneratorAction'
        return info


    def setPID(self, pid):
        if not isinstance(pid, int):
            raise ValueError('PID must be integer')
        self.pid = pid
        
    def GeneratePrimaries(self, event):
        pp = G4.G4PrimaryParticle()
        pp.SetPDGcode(self.pid)

        pp.SetMomentumDirection(self.beam_direction)
        pp.SetTotalEnergy(self.energy)

        v = G4.G4PrimaryVertex()
        self.SetPosition(v)
        v.SetPrimary(pp)

        event.AddPrimaryVertex(v)
    
class GenieGeneratorAction(VlenfGeneratorAction):
    """Generate events from a Genie ntuple"""

    def __init__(self, nevents, pid, energy_distribution):
        VlenfGeneratorAction.__init__(self)
        self.energy_distribution = energy_distribution
        self.pid = pid
        self.nevents = nevents
        
        self.event_list = self.get_next_events()

        self.generate_file()

        self.mc_info = None  # Info on what is simulated

    def __del__(self):
        os.remove(self.filename)

    def getMCInfo(self):
        return self.mc_info

    def generate_file(self):
        id, filename = tempfile.mkstemp(suffix='.root')

        fake_run = random.randint(1, sys.maxint) # avoids race conditions
        seed = random.randint(1, sys.maxint)

        max_energy = 5.0

        env_vars = 'GSPLOAD=data/xsec.xml GSEED=%d' % seed

        command = '%s gevgen' % env_vars

        command += ' -p %d' % self.pid
        command += ' -r %d' % fake_run
        command += ' -t 1000260560'
        command += ' -n %d' % self.nevents

        if self.energy_distribution == 'm':
            command += ' -e 0.1,%f -f data/flux_file_mu.dat' % max_energy
        elif self.energy_distribution == 'e':
            command += ' -e 0.1,%f -f data/flux_file_e.dat' % max_energy
        elif type(self.energy_distribution) == float:
            command += ' -e %f' % self.energy_distribution
        else:
            raise ValueError('bad energy distribution')

        command += ' > /dev/null' # shut it up

        self.log.critical('Running the command: %s', command)
        
        os.system(command)
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
                assert(t.__getattr__('nc') == 1)
                lepton_event['code'] = self.pid
            elif t.__getattr__('nc') == 1:
                raise ValueError()
            else:
                lepton_event['code'] = lookup_cc_partner(self.pid)

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

            event_type['incoming_neutrino'] = t.__getattr__('neu')
            event_type['neutrino_energy'] = t.__getattr__('Ev')
            
            yield next_events, event_type

    def GeneratePrimaries(self, event):
        particles, event_type = next(self.event_list)

        self.mc_info = {'particles' : particles, 'event_type' : event_type}

        for particle in particles:
            pp = G4.G4PrimaryParticle()
            self.log.debug('Adding particle with PDG code %d' % particle['code'])
            pp.SetPDGcode(particle['code'])

            particle['px'], particle['py'], particle['pz'] = \
                [1000 * x for x in [particle['px'], particle['py'],
                                    particle['pz']]]  # GeV -> MeV

            pp.SetMomentum(particle['px'], particle['py'], particle['pz'])

            v = G4.G4PrimaryVertex()
            self.SetPosition(v)
            v.SetPrimary(pp)

            event.AddPrimaryVertex(v)

    
