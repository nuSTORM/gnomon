"""Add truth values to data stream"""

import logging
import sys

class AppendTruth:
    def __init__(self, pga, TA):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.log.debug('Truth store initialized')

        self.pga = pga
        self.ta = TA

        self.enabled = True
        try:
            self.pga.getMCInfo()
        except AttributeError:
            self.log.warning('Disabling: no MC info in GeneratorAction')
            self.enabled = False

        try:
            self.ta.FetchThenClear()
        except AttributeError:
            pass
        #self.log.warning('Disabling: no MC info in GeneratorAction')
        #    self.enabled = False
        
    def Shutdown(self):
        pass

    def Process(self, docs):
        # Do nothing if no MC information is avaiable
        if not self.enabled:
            return docs

        # Otherwise get info from Generator Action
        new_docs = []
        for doc in docs:
            doc['mc'] = self.pga.getMCInfo()
            #doc['mc']['tracking'] = self.ta.FetchThenClear()
            new_docs.append(doc)
        return new_docs

