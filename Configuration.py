"""Store configuration information for the run"""

import Geant4 as G4
import couchdb

class CouchConfiguration():
    def __init__(self, run):
        self.couch = couchdb.Server('http://gnomon:VK0K1QMQ@localhost:5984/')

        self.db_name = "test"

        if self.db_name in self.couch:
            print 'WARNING: Already found DB %s' % self.db_name
            #self.couch.delete(self.db_name)
            self.db = self.couch[self.db_name]
        else:
            self.db = self.couch.create(self.db_name)

        map_fun = """
function(doc) {
  if (doc.type == 'configuration'){
    if (doc.run == %d){
           emit(doc.run, doc);
    }
  }
}
""" % run

        self.configuration = None
        my_query = self.db.query(map_fun)
        if len(my_query) > 1:
            print "ERROR!"
        elif len(my_query) == 1:
            self.configuration = list(my_query)[0].value
            print self.configuration

        else:
            self.configuration = {}
            self.configuration['type'] = 'configuration'
            self.configuration['event'] = -1 # negative event number means unset
            self.configuration['run'] = run

        self.db.save(self.configuration)

    def getCouchDB(self):
        return self.couch

    def getCurrentDB(self):
        return self.db

    def getRunNumber(self):
        return self.run_number

    def setEventNumber(self, number):
        self.configuration['event'] = number
        self.db.save(self.configuration)

    def getEventNumber(self):
        self.db.save(self.configuration)
        return self.configuration['event']

DEFAULT = CouchConfiguration
