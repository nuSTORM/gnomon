"""Routines to save output
"""


import os
import sys
import couchdb
import gnomon.Configuration as Configuration
from gnomon.processors import Base


class Manager(Base.Processor):  # pylint: disable-msg=R0922
    """Output base class
    """
    def __init__(self):
        Base.Processor.__init__(self)
        self.config = Configuration.GLOBAL_CONFIG
        self.log.debug('Config:')
        self.log.debug(self.config)
        assert self.config

    def save(self, doc):  # pylint: disable-msg=C0111
        raise NotImplementedError

    def shutdown(self):  # pylint: disable-msg=C0111
        pass

    def process(self, docs):
        """Loop over docs and save each"""
        for doc in docs:
            self.save(doc)


class CouchManager(Manager):
    """Output to CouchDB

    This class handles sending events to CouchDB.
    """

    def __init__(self):
        """Initialize

        Setup connect to Couch
        """
        Manager.__init__(self)

        self.server_url = self.config['couchdb']['url']

        if os.getenv('COUCHDB_URL'):
            value = os.getenv('COUCHDB_URL')
            self.log.info('Environmental variable COUCHDB_URL: %s' % value)
            self.server_url = value

        self.server = couchdb.Server(self.server_url)
        self.server.version()

        self.my_db = self.setup_db(self.server, self.config['name'])
        self.commit_threshold = self.config['couchdb']['commit_threshold']
        self.docs = []

    def setup_db(self, couch, dbname):
        """Setup and configure DB
        """

        # Avoid race condition of two creating db
        my_db = None

        self.log.debug('Setting up DB: %s' % dbname)

        if dbname not in couch:
            self.log.info("DB doesn't exist so creating DB: %s", dbname)
            try:
                my_db = couch.create(dbname)
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

                my_db.save(auth_doc)
            except:
                self.log.error('Could not set permissions of %s' % dbname)

        else:
            my_db = couch[dbname]

        return my_db

    def commit(self, force=False):
        """Commit data to couchdb

        Compared to threshold (unless forced) then sends data to couch
        """
        self.log.debug('Bulk commit requested')
        size = sys.getsizeof(self.docs)

        self.log.debug('Size of docs in KB: %d', size)
        if size > self.commit_threshold or force:
            self.log.info('Commiting %d KB to CouchDB' % size)
            self.my_db.update(self.docs)
            self.docs = []

    def save(self, doc):
        """Save a doc to cache
        """
        self.log.debug('save()')
        self.docs.append(doc)
        self.commit()

    def shutdown(self):
        """Shutdown and commit rest
        """
        self.log.debug('shutdown()')
        self.commit(force=True)
