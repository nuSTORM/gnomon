"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""

import logging
import sys

import Configuration

class VlenfSimpleDigitizer():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.DEFAULT()
        self.commit_threshold = self.config.getCommitThreshold() 

        self.energy_scale = 80.0 # pe / MeV
        self.log.debug('Energy scale: %f', self.energy_scale)

        self.db = self.config.getCurrentDB()
        
        self.digits = []

        self.threshold = None
        self.setThreshold()


    def Process(self):
        hits_dict = {}

        map_fun = """
function(doc) {
if (doc.type == 'mchit' && doc.number_run == %d)
emit([doc.number_run, doc.number_event, doc.layer, doc.bar, doc.view, doc.position_bar], doc.dedx);
 }""" % self.config.getRunNumber()

        red_fun = """
        function(keys, values, rereduce) {
        return sum(values);
        }"""

        for row in self.db.query(map_fun, red_fun, group=True):
            number_run, number_event, layer, bar, view, position_bar = row.key

            dedx = row.value
            counts_adc = dedx * self.energy_scale
            
            if counts_adc > self.getThreshold():
                digit = {}
                digit['type'] = 'digit'
                digit['number_run'] = number_run
                digit['number_event'] = number_event
                digit['layer'] = layer
                digit['bar'] = bar
                digit['view'] = view
                digit['counts_adc'] = counts_adc
                digit['position'] = position_bar  # this should be derived
                
                self.digits.append(digit)

                print digit, row.key

        self.bulkCommit()

    def setThreshold(self, threshold = 2):
        """Threshold for registering a hit

        Units are ADC counts"""
        self.threshold = threshold

    def getThreshold(self):
        return self.threshold

    def bulkCommit(self, force=False):
        self.log.info('Bulk commit of digits requested')
        size = sys.getsizeof(self.digits)
        self.log.debug('Size of digit bulk commit in bytes: %d', size)
        if size > self.commit_threshold or force:
            self.log.info('Commiting %d bytes to CouchDB' % size)
            self.db.update(self.digits)
            self.digits = []
