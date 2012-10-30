"""Create a ROOT file from a Schema and JSON output"""

import ROOT
import Base
from collections import Mapping, Set, Sequence
from gnomon.JsonToROOT import JsonToROOTConverter

class CreateROOTBase(Base.Processor):
    """Base class for ROOT file creating
    """

    def __init__(self, schema):
        Base.Processor.__init__(self)
        self.conv = JsonToROOTConverter(schema)

    def get_schema(self):
        """Fetch the Schema

        This function must be overloaded
        """
        raise NotImplementedError()

    def process(self, docs):
        for doc in docs:
            self.conv.Process(doc)
        return docs


    def shutdown(self):
        self.conv.Shutdown()

class CreateROOTDigitizedHits(CreateROOTBase):
    """Create ROOT file of digitized hits
    """
    def __init__(self):
        self.schema = {
            "type" : "object",
            "properties" : {
                "run" : {
                    "type" : "number",
                    "description" : "runnumber",
                    },
                "event" : {
                    "type" : "number",
                    "description" : "eventnumber",
                    },
                "classification" : {
                    "type":"object",
                    "properties" : {
                        "n_planes" : {
                            "type" : "number",
                            "description" : "n_planes",
                            }
                        }
                    },
                "digitized_hits": {
                    "type":"object",
                    "properties" : {
                        "xview" : {
                            "type":'object',
                            "properties" : {
                                'x' : {
                                    'type' : 'array',
                                    'description' : 'xview_x'
                                    },
                                'z' : {
                                    'type' : 'array',
                                    'description' : 'xview_z'
                                    },
                                'adc' : {
                                    'type' : 'array',
                                    'description' : 'xview_adc'
                                    }
                                }
                            },
                        "yview" : {
                            "type":'object',
                            "properties" : {
                                'y' : {
                                    'type' : 'array',
                                    'description' : 'yview_y'
                                    },
                                'z' : {
                                    'type' : 'array',
                                    'description' : 'yview_z'
                                    },
                                'adc' : {
                                    'type' : 'array',
                                    'description' : 'yview_adc'
                                    }
                                }
                            }
                        }
                    },
                'mc' : {
                    'type' : 'object',
                    'properties' : {
                        'event_type' : {
                            'type' : 'object',
                            'properties' : {
                                'vertex' : {
                                    'type' : 'object',
                                    'properties' : {
                                        'x' : {
                                            'type' :'number',
                                            'description' : 'interaction_x'
                                            },
                                        'y' : {
                                            'type' :'number',
                                            'description' : 'interaction_y'
                                            },
                                        'z' : {
                                            'type' :'number',
                                            'description' : 'interaction_z'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }


        CreateROOTBase.__init__(self, self.schema)
        
