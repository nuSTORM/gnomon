"""Store configuration information for the run"""

import Geant4 as G4
import couchdb

class LocalConfiguration():
    def __init__(self):
        self.couch = couchdb.Server('http://gnomon:VK0K1QMQ@localhost:5984/')
        self.run_number = -100
        self.sd = None

    def getCouchDB(self):
        return self.couch

    def Process(self, hits):

DEFAULT = LocalConfiguration
