"""Store configuration information for the run"""

import Geant4 as G4
import couchdb
import os
import logging

# Run number, needs to be set by initializing process
run = 0
name = "test"

class CouchConfiguration():
    def __init__(self):
        self.server_url = 'http://localhost:5984/'
        if os.getenv('COUCHDB_URL'):
            value = os.getenv('COUCHDB_URL')
            logging.info('Using environmental variable COUCHDB_URL: %s' % value)
            self.server_url = value

        self.couch = couchdb.Server(self.server_url)
        self.couch.version()
        #self.couch = couchdb.Server('http://gnomon:VK0K1QMQ@gnomon.iriscouch.com/')

        if name in self.couch:
            print 'WARNING: Already found DB %s' % name
            #self.couch.delete(name)
            self.db = self.couch[name]
        else:
            self.db = self.couch.create(name)

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
