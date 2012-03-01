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
        """Setup the CouchDB configuration manager.

        The default connection is to localhost's port 5984.  This can be
        overridden by setting the environmental variable COUCHDB_URL to,
        for example, http://new_server:1234/"""


        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.server_url = 'http://localhost:5984/'
        if os.getenv('COUCHDB_URL'):
            value = os.getenv('COUCHDB_URL')
            self.log.info('Using environmental variable COUCHDB_URL: %s' % value)
            self.server_url = value

        self.couch = couchdb.Server(self.server_url)
        self.couch.version()  # check that CouchDB connection works

        if name in self.couch:
            self.debug('DB already exists: %s', name)
            self.db = self.couch[name]
        else:
            self.debug('Creating DB: %s', name)
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
            self.log.critical("Too many configurations for run %d. Grabbing first. This should never happen.", run)

        if len(my_query) != 0:
            self.configuration = list(my_query)[0].value
            self.log.debug('The configuraiton is: %s', self.configuration)
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
