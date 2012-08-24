"""Base class for processors
"""


import logging
from gnomon import Configuration


class Processor():
    """Base call for all processors

    Defines the API for processors
    """

    def __init__(self):
        """Setup logging"""
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.GLOBAL_CONFIG

    def process(self, docs):
        """Not implemented"""
        raise NotImplementedError

    def shutdown(self):
        """Do nothing"""
        pass
