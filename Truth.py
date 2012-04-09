"""Add truth values to data stream"""

import logging
import sys

class AppendTruth:
    def __init__(self, pga):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.log.debug('Truth store initialized')

        self.pga = pga
        
    def Shutdown(self):
        pass

    def Process(self, docs):
        new_docs = []
        for doc in docs:
            doc['mc'] = self.pga.getMCInfo()
            new_docs.append(doc)

        return new_docs
