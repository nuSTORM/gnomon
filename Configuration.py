"""Store configuration information for the run"""

import couchdb
import os
import logging

# Run number, needs to be set by initializing process
run = 0
name = ""

class CouchConfiguration():
    def __init__(self, warn_if_exists = False):
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
            if warn_if_exists:
                self.log.warning('DB already exists: %s', name)
            else:
                self.log.info('DB already exists: %s', name)

        # Avoid race condition of two creating db
        if name not in self.couch:
            self.log.info("DB doesn't exist so creating DB: %s", name)
            try:
                db = self.couch.create(name)
                auth_doc = {}
                auth_doc['_id'] = '_design/auth'
                auth_doc['language'] = 'javascript'
                auth_doc['validate_doc_update'] = """
                function(newDoc, oldDoc, userCtx) {
                if (userCtx.roles.indexOf('_admin') !== -1) {
                return;
                } else {
                throw({forbidden: 'Only admins may edit the database'});
                }
                }
                """
                db.save(auth_doc)
            except:
                pass

        self.db = self.couch[name]

        self.map_fun = """
function(doc) {
  if (doc.type == 'configuration'){
    if (doc.run == %d){
           emit(doc.run, doc);
    }
  }
}
""" % run

    def getCouchDB(self):
        return self.couch

    def getCurrentDB(self):
        return self.db

    def getRunNumber(self):
        return run
        

class MockDB():
    def update(self, doc):
        pass

    def save(self, doc):
        pass

class MockConfiguration():
    def __init__(self):
        self.db = MockDB()

    def getCouchDB(self):
        raise NotImplementedError

    def getCurrentDB(self):
        return self.db

    def getRunNumber(self):
        return 0
    

DEFAULT = CouchConfiguration
