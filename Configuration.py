"""Store configuration information for the run"""

import Geant4 as G4
import couchdb

# Run number, needs to be set by initializing process
run = 0

class CouchConfiguration():

    def __init__(self):
        self.couch = couchdb.Server('http://gnomon:VK0K1QMQ@localhost:5984/')

        self.db_name = "test"

        if self.db_name in self.couch:
            print 'WARNING: Already found DB %s' % self.db_name
            #self.couch.delete(self.db_name)
            self.db = self.couch[self.db_name]
        else:
            self.db = self.couch.create(self.db_name)

        self.map_fun = """
function(doc) {
  if (doc.type == 'configuration'){
    if (doc.run == %d){
           emit(doc.run, doc);
    }
  }
}
""" % run

        self.configuration = None
        my_query = self.db.query(self.map_fun)
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
        return run

    def setEventNumber(self, number):
        my_query = self.db.query(self.map_fun)
        assert len(my_query) == 1
        self.configuration = list(my_query)[0].value
        self.configuration['event'] = number
        self.db.save(self.configuration)

    def getEventNumber(self):
        my_query = self.db.query(self.map_fun)
        assert len(my_query) == 1
        self.configuration = list(my_query)[0].value
        return self.configuration['event']


DEFAULT = CouchConfiguration
