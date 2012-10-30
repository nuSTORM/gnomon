"""Interface to Recpack's Kalman Filtering via mind_rec"""

from gnomon.processors import Base
from gnomon import JsonToROOT
import validictory

class RecpackFitter(Base.Processor):
    """Use Recpack's Kalman Filter for reconstruction

    MindRec will take as an input on an event by event basis (where the
    Genie gst code is specified when available):

    * Event vertex (x,y,z) [mm] - determine ourselves (not Genie)
    * Genie interaction type - (gst: 'nuance')
    * Produces charm [bool] - (gst: 'charm')
    * Charm hadron (pdg designation)
    * Q^2 (GENIE Kine.Q2(true)*GeV) (gst: 'Q2')
    * neutrino type (pdg)
    * neutrino energy [GeV]
    * Nucleus type (pdg)
    * Nucleus energy [GeV]
    * interaction particle (pdg)
    * interaction particle Energy [GeV]
    * Hadron 4 vector -- (px, py, pz, E) from sum of all final state particles excluding the final state lepton [GeV]

    For a single hit, MindRec requires

    * hit position (x,y,z) [mm]
    * energy deposition [MeV]
    """

    def __init__(self):
        self.schema = {
            'type' : 'object',
            'properties' : {
                'run' : {
                    'type' :'number',
                    'description' : 'runnumber'
                    },
                'mc' : {
                    'type' : 'object',
                    'properties' : {
                        'event_type' : {
                            'type' : 'object',
                            'properties' : {
                                'vertex' : {
                                    'type' : 'object',
                                    'properties' : {
                                        'x' : {
                                            'type' :'number',
                                            'description' : 'interaction_x'
                                            },
                                        'y' : {
                                            'type' :'number',
                                            'description' : 'interaction_y'
                                            },
                                        'z' : {
                                            'type' :'number',
                                            'description' : 'interaction_z'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

        self.converter = JsonToRootConverter(self.schema)


    def process(self, docs):
        for doc in docs:
            if doc['analyzable']:
                validictory.validate(doc, self.schema)

                self.converter.Process(doc)
                print 'pass'

        return docs

    def shutdown(self):
        self.converter.Shutdown()
