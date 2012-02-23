import Geant4 as G4
import ROOT

class GenieGeneratorAction(G4.G4VUserPrimaryGeneratorAction):
    "My Primary Generator Action"

    def __init__(self):
        G4.G4VUserPrimaryGeneratorAction.__init__(self)
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
            for type in ['qel', 'res', 'dis', 'coh', 'dfr', 'imd', 'nuel', 'em'\
]:
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
        events = next(self.event_list)
        for particle in events:
            pp = G4.G4PrimaryParticle()
            pp.SetPDGcode(particle['code'])

            particle['px'], particle['py'], particle['pz'] = [1000*x for x in [\
particle['px'], particle['py'], particle['pz']]]  # GeV -> MeV                  

            pp.SetMomentum(particle['px'], particle['py'], particle['pz'])

            v = G4.G4PrimaryVertex()
            v.SetPosition(20.0, 20.0, 0.0)
            v.SetPrimary(pp)

            event.AddPrimaryVertex(v)
