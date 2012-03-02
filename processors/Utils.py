"""Compactor"""

import logging

import couchdb

import Configuration

class Compactor():
    """empty"""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.DEFAULT()
        self.db = self.config.getCurrentDB()

        self.interval = 10


    def __del__(self):
        self.log.debug('Destructor is compacting DB.  Successful = %s', str(self.db.compact()))

    def FetchThenProcess(self, run, event):
        if event % self.interval == -1 % self.interval:
            self.log.debug('Compacting DB.  Successful = %s', str(self.db.compact()))
