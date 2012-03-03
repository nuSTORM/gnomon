"""Generator actions

These generate particles to simulate"""

import Geant4 as G4
import ROOT

import logging

class SingleParticleGeneratorAction(G4.G4VUserPrimaryGeneratorAction):
    """Generate single particle at specific point"""
    def __init__(self):
        G4.G4VUserPrimaryGeneratorAction.__init__(self)

    def GeneratePrimaries(self, event):
        pp = G4.G4PrimaryParticle()
        pp.SetPDGcode(particle['code'])

        pp.SetMomentum(0, 0, 0.5) # GeV/c

        v = G4.G4PrimaryVertex()
        v.SetPosition(0.0, 1000.0 * G4.mm, 0)
        v.SetPrimary(pp)

        event.AddPrimaryVertex(v)
    
class GenieGeneratorAction(G4.G4VUserPrimaryGeneratorAction):
    """Generate events from a Genie ntuple"""

    def __init__(self):
        G4.G4VUserPrimaryGeneratorAction.__init__(self)
        self.event_list = self.get_next_events()

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

    def get_next_events(self):
        f = ROOT.TFile('ntuple_neg14.root')
        t = f.Get('gst')

        n = t.GetEntries()

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

            self.log.debug('Event type:')
            for type in ['qel', 'res', 'dis', 'coh', 'dfr',
                         'imd', 'nuel', 'em']:
                self.log.debug('\t%s:%d', type, t.__getattr__(type))

            self.log.debug('Propogator:')
            for prop in ['nc', 'cc']:
                self.log.debug('\t%s:%d', prop, t.__getattr__(prop))

            self.log.debug('y: %f', t.y)
            try:
                self.log.debug('m_l: %f', math.sqrt(t.El ** 2 -
                                        (t.pxl ** 2 + t.pyl ** 2 + t.pzl ** 2)))
            except:
                pass

            yield next_events

    def GeneratePrimaries(self, event):
        events = next(self.event_list)
        for particle in events:
            pp = G4.G4PrimaryParticle()
            pp.SetPDGcode(particle['code'])

            particle['px'], particle['py'], particle['pz'] = \
                [1000 * x for x in [particle['px'], particle['py'],
                                    particle['pz']]]  # GeV -> MeV

            pp.SetMomentum(particle['px'], particle['py'], particle['pz'])

            v = G4.G4PrimaryVertex()
            v.SetPosition(0.0, 1000.0 * G4.mm, 0)
            v.SetPrimary(pp)

            event.AddPrimaryVertex(v)
