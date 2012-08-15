"""Generator actions

These classes are used to tell Geant4 what particles it is meant to simulate.
One always has to inherit from a UserPrimaryGeneratorAction base class in
Geant4 and then define the function GeneratePrimaries.
"""

import Geant4 as G4
import ROOT

import logging
import sys
import os
import random
import tempfile
import math
import gnomon.Configuration as Configuration
from gnomon.Configuration import RUNTIME_CONFIG as rc
from scipy.stats.distributions import rv_generic

def lookup_cc_partner(nu_pid):
    """Lookup the charge current partner

    Takes as an input neutrino nu_pid is a PDG code, then returns
    the charged lepton partner.  So 12 (nu_e) returns 11.  Keeps sign
    """

    neutrino_type = math.fabs(nu_pid)
    assert neutrino_type in [12, 14, 16]

    cc_partner = neutrino_type - 1  # get e, mu, tau
    cc_partner = math.copysign(
        cc_partner, nu_pid)  # make sure matter/antimatter
    cc_partner = int(cc_partner)  # convert to int

    return cc_partner

def convert_3vector_to_dict(value):
    if not isinstance(value, list):
        raise ValueError('Wrong type for 3-vector since not list', value)
    if len(value) != 3:
        raise ValueError('Wrong dimensions for 3-vector')
    
    new_dict = {}
    new_dict['x'] = value[0]
    new_dict['y'] = value[1]
    new_dict['z'] = value[2]
    
    return new_dict

def convert_dict_to_g4vector(value, new_vector=G4.G4ThreeVector()):
    new_vector.x = value['x']
    new_vector.y = value['y']
    new_vector.z = value['z']
    
    return new_vector

        
class VlenfGeneratorAction(G4.G4VUserPrimaryGeneratorAction):
    """Geant4 interface class"""
    def __init__(self, generator):
        G4.G4VUserPrimaryGeneratorAction.__init__(self)

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.particle_generator = generator

        self.config = Configuration.GLOBAL_CONFIG


    def setMCInfo(self, info):
        rc['generator'] = info

    def GeneratePrimaries(self, event):
        particle = self.particle_generator.generate()

        pp = G4.G4PrimaryParticle()
        pp.SetPDGcode(particle['pid'])

        pp.SetMomentum(particle['momentum']['x'],
                       particle['momentum']['y'],
                       particle['momentum']['z'])

        v = G4.G4PrimaryVertex()
        convert_dict_to_g4vector(particle['position'], v)
        v.SetPrimary(pp)

        event.AddPrimaryVertex(v)

        self.setMCInfo(particle)


class Distribution():
    def __init__(self, some_obj):
        self.static_value = None
        self.scipy_dist = None

        if isinstance(some_obj, (float, int)):
            self.static_value = some_obj
        elif isinstance(some_obj, rv_generic):
            self.scipy_dist = some_obj
        else:
            raise ValueError("Do not understand", some_obj)


    def get(self):
        if self.static_value is not None:
            return self.static_value
        elif self.scipy_dist is not None:
            return rv_generic.rvs()
        else:
            raise RuntimeError("Should never get here")


class ParticleGenerator():
    """Baseclass for gnomon particle generators"""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.particle = {}
        self.particle['position'] = None
        self.particle['momentum'] = None
        self.particle['pid'] = None


    def set_particle(self, position, momentum, pid):
        self.set_position(position)
        self.set_momentum(momentum)
        self.set_pid(pid)

    def set_position(self, position):
        self._set_vector_value('position', position)

    def set_momentum(self, momentum):
        self._set_vector_value('momentum', momentum)

    def _set_vector_value(self, var_name, value):
        self.particle[var_name] = convert_3vector_to_dict(value)

        for coord in self.particle[var_name].keys():
            new_value = Distribution(self.particle[var_name][coord])
            self.particle[var_name][coord] = new_value

    def set_pid(self, pid):
        assert isinstance(pid, int)
        self.particle['pid'] = Distribution(pid)

    def generate(self):
        new_particle = {}

        for key, value in self.particle.iteritems():
            if isinstance(value, dict):  # restricts 2 depth, recurse instead?
                new_particle[key] = {}

                for key2, value2 in value.iteritems():
                    new_particle[key][key2] = value2.get()
            else:    
                new_particle[key] = value.get()

        self.log.info("Generated particle:", new_particle)
        
        return new_particle




class GenieGeneratorAction(VlenfGeneratorAction):
    """Generate events from a Genie ntuple"""

    def __init__(self, pid, energy_distribution):
        VlenfGeneratorAction.__init__(self)
        self.energy_distribution = energy_distribution
        self.pid = pid

         #  The event list is a generator so requires calling 'next' on it
        self.event_list = None  # set by generate_file

        self.generate_file()

    def __del__(self):
        os.remove(self.filename)

    def generate_file(self):
        id, filename = tempfile.mkstemp(suffix='.root')

        seed = random.randint(1, sys.maxint)

        max_energy = self.config['generator']['max_energy_GeV']

        env_vars = 'GSPLOAD=data/xsec.xml GSEED=%d' % seed

        command = '%s gevgen' % env_vars

        command += ' -p %d' % self.pid
        command += ' -r %d' % self.config['run_number']
        command += ' -t 1000260560'
        command += ' -n %d' % self.config['generator']['size_of_genie_buffer']

        if self.energy_distribution == 'm':
            command += ' -e 0.1,%f -f data/flux_file_mu.dat' % max_energy
        elif self.energy_distribution == 'e':
            command += ' -e 0.1,%f -f data/flux_file_e.dat' % max_energy
        elif type(self.energy_distribution) == float:
            command += ' -e %f' % self.energy_distribution
        else:
            raise ValueError('bad energy distribution')

        command += ' > /dev/null'  # shut it up

        self.log.info('Running the command: %s', command)

        os.system(command)
        os.system("gntpc -i gntp.%d.ghep.root -o %s -f gst > /dev/null" %
                  (self.config['run_number'], filename))
        os.system('rm gntp.%d.ghep.root' % self.config['run_number'])
        self.filename = filename

        self.event_list = self.get_next_events()

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
                lepton_event['code'] = self.pid  # Either NC or ES
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
        try:
            particles, event_type = next(self.event_list)
        except StopIteration:
            self.log.info("Generating more Genie events")
            self.generate_file()
            particles, event_type = next(self.event_list)

        rc['generator'] = {'particles': particles, 'event_type': event_type}

        for particle in particles:
            pp = G4.G4PrimaryParticle()
            self.log.debug(
                'Adding particle with PDG code %d' % particle['code'])
            pp.SetPDGcode(particle['code'])

            particle['px'], particle['py'], particle['pz'] = \
                [1000 * x for x in [particle['px'], particle['py'],
                                    particle['pz']]]  # GeV -> MeV

            pp.SetMomentum(particle['px'], particle['py'], particle['pz'])

            v = G4.G4PrimaryVertex()
            self.SetPosition(v)
            v.SetPrimary(pp)

            event.AddPrimaryVertex(v)
