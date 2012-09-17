"""Add truth values to data stream"""


from gnomon.processors import Base
from gnomon.Configuration import RUNTIME_CONFIG as rc


class AppendTruth(Base.Processor):
    def __init__(self):
        Base.Processor.__init__(self)

        self.log.debug('Truth store initialized')

    def process(self, docs):
        new_docs = []
        for doc in docs:
            doc['mc'] = {}

            # Persistent
            for name in ['field']:
                doc['mc'][name] = rc[name]
                if name in rc:
                    doc['mc'][name] = rc[name]

            # Nonpersistent
            for name in ['generator',
                         'tracking',
                         'event_type']:
                if name in rc:
                    doc['mc'][name] = rc[name]
                    rc[name] = {}  # must reset!

            new_docs.append(doc)
        return new_docs
