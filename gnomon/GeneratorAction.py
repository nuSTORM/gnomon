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
import subprocess
import math
import gnomon.Configuration as Configuration
from gnomon.Configuration import RUNTIME_CONFIG as rc
from scipy.stats.distributions import rv_frozen
import scipy


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


def is_neutrino_code(pdg_code):
    if math.fabs(pdg_code) in [12, 14, 16]:
        return True
    return False


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
        particles = self.particle_generator.generate()

        for particle in particles:
            pp = G4.G4PrimaryParticle()
            pp.SetPDGcode(particle['pid'])

            pp.SetMomentum(particle['momentum']['x'],
                particle['momentum']['y'],
                particle['momentum']['z'])

            v = G4.G4PrimaryVertex()
            v.SetPosition(particle['position']['x'],
                particle['position']['y'],
                particle['position']['z'])

            v.SetPrimary(pp)

            event.AddPrimaryVertex(v)

        # Write particleS information to the runtime configuration so the Truth
        #  processor can find it in order to output it
        self.setMCInfo(particles)


class composite_z():
    """Deriving from scipy.stats failed, so just overloaded rvs.
    This really should hook into the GDML or something since it is geo
    dependent this way"""

    def __init__(self, config):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.layers = config['layers']
        self.z_extent = config['layers'] * config['thickness_layer']
        self.thickness_layer = config['thickness_layer']
        self.thickness_bar = config['thickness_bar']

        self.density = {}
        self.density['Iron'] = config['density_iron']
        self.density['Scint.'] = config['density_scint']

        self.material = None

    def get_material(self):  # hack for Genie to know material
        """Return material of last rvs call"""
        return self.material

    def rvs(self):
        layer = random.randint(-self.layers / 2, self.layers / 2 - 1)  # inclusive

        d_sc = self.density['Scint.']
        t_sc = 2 * self.thickness_bar

        t_fe = self.thickness_layer - t_sc
        d_fe = self.density['Iron']

        z = layer * self.thickness_layer

        # How much material is there
        my_max = t_fe * d_fe + t_sc * d_sc

        # Choose random by gram
        my_choice = random.uniform(0, my_max)

        if my_choice < t_fe * d_fe:  # Is iron
            z += random.uniform(0, t_fe)
            self.material = 'Iron'
        else:  # is scint
            z += t_fe
            z += random.uniform(0, t_sc)
            self.material = 'Scint.'

        #self.log.debug('Material is %s' % self.material)
        return z


class Distribution():
    def __init__(self, some_obj):
        self.static_value = None
        self.scipy_dist = None

        if isinstance(some_obj, (float, int)):
            self.static_value = some_obj
        elif hasattr(some_obj, 'rvs'):
            self.scipy_dist = some_obj
        else:
            raise ValueError("Do not understand", some_obj)

        self.cache = None

    def dist(self):
        #  Horrible HACK.  Since we don't have Genie know about GDML we have
        # to let GenieGenerator have a hook to know what material to simulate
        if self.scipy_dist is None:
            return None
        return self.scipy_dist

    def is_static(self):
        if self.static_value is not None:
            return True
        return False

    def get_cache(self):
        return self.cache

    def set_cache(self, value):
        self.cache = value

    def get(self):
        if self.static_value is not None:
            self.set_cache(self.static_value)
        elif self.scipy_dist is not None:
            self.set_cache(self.scipy_dist.rvs())
        else:
            raise RuntimeError("Should never get here")

        return self.get_cache()


class Generator():
    """Generator base class"""

    def __init__(self, position, momentum, pid):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
        self.log.debug('Initialized %s', self.__class__.__name__)

        self.config = Configuration.GLOBAL_CONFIG

        self.particle = {}

        self.set_position(position)
        self.set_momentum(momentum)
        self.set_pid(pid)  # Can be neutrino with forced interaction

    def set_position(self, position):
        self._set_vector_value('position', position)

    def set_momentum(self, momentum):
        self._set_vector_value('momentum', momentum)

    def set_pid(self, pid):
        assert isinstance(pid, int)
        self.particle['pid'] = Distribution(pid)

    def _set_vector_value(self, var_name, value):
        """Private"""
        self.particle[var_name] = convert_3vector_to_dict(value)

        for coord in self.particle[var_name].keys():
            new_value = Distribution(self.particle[var_name][coord])
            self.particle[var_name][coord] = new_value


class ParticleGenerator(Generator):
    """Baseclass for gnomon particle generators"""

    def __init__(self, position, momentum, pid):
        Generator.__init__(self, position, momentum, pid)

    def generate(self):
        new_particle = {}

        for key, value in self.particle.iteritems():
            if isinstance(value, dict):  # restricts 2 depth, recurse instead?
                new_particle[key] = {}

                for key2, value2 in value.iteritems():
                    new_particle[key][key2] = value2.get()
            else:
                new_particle[key] = value.get()

        self.log.info("Generated particle:")
        self.log.info(new_particle)

        return [new_particle]


class GenieGenerator(Generator):
    """Generate events from a Genie ntuple

    A Genie ntuple that already knew the GDML would be useful.  Otherwise,
    we run gevgen per material and have to do nasty geometry stuff here
    """

    def __init__(self, position, momentum, pid):
        Generator.__init__(self, position, momentum, pid)

        #  The event list is a generator so requires calling 'next' on it.
        # The key is a material 'Iron', 'Scint.'  etc
        self.event_list = {}
        self.filenames = {}

        self.genie_temp_dir = tempfile.mkdtemp()

    def __del__(self):
        for key in self.filenames.keys():
            os.remove(self.filenames[key])

        os.rmdir(self.genie_temp_dir)

    def _create_file(self, material):
        my_id, filename = tempfile.mkstemp(suffix='.root')

        seed = random.randint(1, sys.maxint)

        max_energy = self.config['generator']['max_energy_GeV']

        xsec_filename = os.path.join(self.config['data_dir'], 'xsec.xml')

        #  Environmental variables need to be set to tell Genie where cross
        # section files are and a repeatable random number seed. Also, disable
        # any X windows popping up (was causing crashes...)
        env_vars = 'DISPLAY= GSPLOAD=%s GSEED=%d' % (xsec_filename, seed)

        command = '%s gevgen' % env_vars

        command += ' -p %d' % self.particle['pid'].get()
        command += ' -r %d' % self.config['run_number']

        pdg_codes = {}
        pdg_codes['Iron'] = '1000260560'
        pdg_codes['Scint.'] = '1000010010[0.085]+1000060120[0.915]'

        command += ' -t %s' % pdg_codes[material]

        command += ' -n %d' % self.config['generator']['size_of_genie_buffer']

        self.energy_distribution = self.config['distribution']
        self.log.info('Neutrino energy distribution: %s' % self.energy_distribution)

        if self.energy_distribution == 'muon' or\
           self.energy_distribution == 'electron' or\
           self.energy_distribution == 'flat':
            # muon, electron, or flat

            command += ' -e 0.1,%f' % max_energy

            #  Just use the file associated with the neutrino distribution of
            #  muon decay without any accelerator effects.  This is a good
            #  approximation in the far detector limit ONLY.
            flux_filename = 'flux_file_%s.dat' % self.energy_distribution[0]
            flux_filename = os.path.join(self.config['data_dir'],
                flux_filename)

            command += ' -f %s' % flux_filename
        elif type(self.energy_distribution) == float:
            command += ' -e %f' % self.energy_distribution
        else:
            raise ValueError('bad energy distribution')

        self.log.info('Running the command: %s', command)

        print filename

        intermediate_file = os.path.join(self.genie_temp_dir,
            "gntp.%d.ghep.root" % self.config['run_number'])

        command = """cd %(tmpdir)s
%(command)s
DISPLAY= gntpc -i %(int_file)s -o %(filename)s -f gst
""" % {"tmpdir": self.genie_temp_dir,
       "command": command,
       "int_file": intermediate_file,
       "filename": filename}

        self.log.info('Running the command: %s', command)

        s = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True) # unsafe, but no easy way TODO

        # Trick to send stdout -> debug
        while True:
            line = s.stdout.readline()
            if not line:
                break
            self.log.debug(line)

        # Trick to send stderr -> error
        while True:
            line = s.stdout.readline()
            if not line:
                break
            self.log.error(line)

        os.remove(intermediate_file)

        self.filenames[material] = filename

        self.event_list[material] = self._get_next_events(material)

    def _get_next_events(self, material):
        """Get next events from Genie ROOT file

        Looks over the generator"""

        f = ROOT.TFile(self.filenames[material])
        try:
            t = f.Get('gst')
            n = t.GetEntries()
        except:
            self.log.critical('Could not open the ROOT file with Genie events')
            raise

        for i in range(n):
            t.GetEntry(i)
            next_events = []

            position = convert_3vector_to_dict([self.particle['position']['x'].get_cache(),
                                                self.particle['position'][
                                                'y'].get_cache(),
                                                self.particle['position']['z'].get_cache()])

            lepton_event = {}
            if t.El ** 2 - (t.pxl ** 2 + t.pyl ** 2 + t.pzl ** 2) < 1e-7:
                lepton_event['pid'] = self.particle[
                                      'pid'].get()  # Either NC or ES
            else:
                lepton_event['pid'] = lookup_cc_partner(
                    self.particle['pid'].get())

            # units: GeV -> MeV
            momentum_vector = [1000 * x for x in [t.pxl, t.pyl, t.pzl]]

            lepton_event['momentum'] = convert_3vector_to_dict(momentum_vector)

            lepton_event['position'] = position

            next_events.append(lepton_event)

            for j in range(t.nf):  # nf, number final hadronic states
                hadron_event = {}
                hadron_event['pid'] = t.pdgf[j]
                hadron_event['position'] = position

                # units: GeV -> MeV
                momentum_vector = [1000 * x for x in [t.pxf[j], t.pyf[j], t.pzf[j]]]

                hadron_event['momentum'] = convert_3vector_to_dict(momentum_vector)

                next_events.append(hadron_event)

            event_type = {}

            to_save = {} # maps our names to Genie gst names
            to_save['incoming_neutrino'] = 'neu'
            to_save['neutrino_energy'] = 'Ev'
            to_save['target_material'] = 'tgt'

            for key, value in to_save.iteritems():
                self.log.info('%s : %s' % (key, str(t.__getattr__(value))))
                event_type[key] = t.__getattr__(value)

            self.log.debug('Event type:')
            for my_type in ['qel', 'res', 'dis', 'coh', 'dfr',
                            'imd', 'nuel', 'em']:
                if t.__getattr__(my_type) == 1:
                    self.log.debug('\t%s', my_type)
                event_type[my_type] = t.__getattr__(my_type)

            self.log.debug('Propogator:')
            for prop in ['nc', 'cc']:
                if t.__getattr__(prop) == 1:
                    self.log.debug('\t%s', prop)
                event_type[prop] = t.__getattr__(prop)

            yield next_events, event_type

        f.Close()
        os.remove(self.filenames[material])

    def generate(self):
        if self.particle['pid'].is_static() == False:
            raise ValueError("PID must be static")

        if not is_neutrino_code(self.particle['pid'].get()):
            raise ValueError("PID must be neutrino PDG code")

        material = 'Iron'

        # More hack: need to know position to know material...
        position = convert_3vector_to_dict([self.particle['position']['x'].get(),
                                            self.particle['position']['y'].get(),
                                            self.particle['position']['z'].get()])

        # Is this a distribution?  Need material hook HACK
        dist = self.particle['position']['z'].dist()
        if dist.__class__.__name__ == 'composite_z':
            material = dist.get_material()
            self.log.info("Choosing material %s" % material)

        if material not in self.event_list:
            self.event_list[material] = None

        try:
            if self.event_list[material] == None:
                self.log.info('Empty event list, populating with Genie...')
                self._create_file(material)

            particles, event_type = next(self.event_list[material])
        except StopIteration:
            self.log.info("Generating more Genie events")
            self._create_file(material)
            particles, event_type = next(self.event_list[material])

        rc['event_type'] = event_type

        return particles
