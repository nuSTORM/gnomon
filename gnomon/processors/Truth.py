"""Add truth values to data stream"""


from gnomon.processors import Base


class AppendTruth(Base.Processor):
    def __init__(self, pga):
        Base.Processor.__init__(self)

        self.log.debug('Truth store initialized')

        self.pga = pga

        self.enabled = True
        try:
            self.pga.getMCInfo()
        except AttributeError:
            self.log.warning('Disabling: no MC info in GeneratorAction')
            self.enabled = False

    def process(self, docs):
        # Do nothing if no MC information is avaiable
        if not self.enabled:
            return docs

        # Otherwise get info from Generator Action
        new_docs = []
        for doc in docs:
            doc['mc'] = self.pga.getMCInfo()
            new_docs.append(doc)
        return new_docs
