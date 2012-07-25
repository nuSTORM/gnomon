"""Store configuration information for the run"""

import os
import logging

from schemas.ConfigurationSchema import schema

class LocalConfiguration(ConfigurationBase):
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
            self.log.info('Environmental variable COUCHDB_URL: %s' % value)
            self.server_url = value

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

        self.setupDB(couch, self.getDBName())
        self.db = couch[self.getDBName()]
        return self.db

    def getRunNumber(self):
        return run

    def getCommitThreshold(self):
        return 1024 # kbytes, ie. 1 MB


class ConfigurationBase():
    """Base class for all configuration classes"""
    def __init__(self, name, run):
        self.name = name
        self.run  = run
        self.json = None

    def setJSON(self, config_json):
        validate(config_json, schema)
        self.json = config_json

    def getCurrentDB(self):
        raise NotImplementedError

    def getConfigurationDict(self):
        raise NotImplementedError


DEFAULT = ProcessConfiguration
