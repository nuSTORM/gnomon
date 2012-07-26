"""Routines to save output
"""


import os
import couchdb
import logging
import Configuration
import sys


class Manager:
    """Output base class
    """
    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.GLOBAL_CONFIG
        self.log.critical(self.config)
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
    def __init__(self):
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
        self.log.debug('Bulk commit requested')
        size = sys.getsizeof(self.docs)

        self.log.debug('Size of docs in KB: %d', size)
        if size > self.commit_threshold or force:
            self.log.info('Commiting %d KB to CouchDB' % size)
            self.my_db.update(self.docs)
            self.docs = []

    def save(self, doc):
        self.log.debug('save()')
        self.docs.append(doc)
        self.commit()

    def shutdown(self):
        self.log.debug('shutdown()')
        self.commit(force=True)
