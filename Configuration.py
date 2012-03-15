"""Store configuration information for the run"""

import couchdb
import os
import logging
import DataManager

# Run number, needs to be set by initializing process
run = 0
name = ""

class ProcessConfiguration():
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

        self.couch = None
        self.db = None


        self.data_manager = None

    def getDataManager(self):
        if not self.data_manager:
            self.data_manager = DataManager.FileManager()
        return self.data_manager

    def getCouchDB(self):
        if self.couch == None:
            self.couch = couchdb.Server(self.server_url)
            try:
                self.couch.version()  # check that CouchDB connection works
            except:
                self.log.critical("Cannot connect to couchdb")
                raise
        return self.couch

    def getDBName(self):
        return name

    def setupDB(self, couch, dbname):
        # Avoid race condition of two creating db
        if dbname not in couch:
                self.log.info("DB doesn't exist so creating DB: %s", dbname)
                try:
                    db = couch.create(dbname)
                except:
                    self.log.error("Race condition caught")

                try:
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
                    self.log.error('Could not set permissions of %s' % dbname)
                    
    def getCurrentDB(self):
        couch = self.getCouchDB()

        if self.db: return self.db # already exists

        if name in self.couch:
            self.log.warning('DB already exists: %s', name)
                
        self.setupDB(couch, self.getDBName())
        self.db = couch[self.getDBName()]
        return self.db

    def getRunNumber(self):
        return run

    def getCommitThreshold(self):
        return 10 * 1024 * 1024 # bytes, ie. 1 MB
        

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

    def getCommitThreshold(self):
        return 1
    

DEFAULT = ProcessConfiguration
