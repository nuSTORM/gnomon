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

        self.energy_scale = 1.0 # pe / MeV
        self.log.debug('Energy scale: %f', self.energy_scale)

        self.db = self.config.getCurrentDB()
        
        self.digits = []

        self.threshold = None
        self.setThreshold()


    def ProcessEvent(self, run):
        hits_dict = {}

        map_fun = """
function(doc) {
if (doc.number_run == %d && doc.type == 'mchit')
emit(doc.type, doc);
 }""" % (run)

        for row in self.db.query(map_fun):
            doc = row.value

            i = doc['layer']
            j = doc['bar']

            if (i,j) not in hits_dict:
                hits_dict[(i,j)] = []

            hits_dict[(i,j)].append(dict(doc))

        for key in hits_dict:
            self.ProcessHits(key, hits_dict[key])

        self.Commit()

    def setThreshold(self, threshold = 2):
        """Threshold for registering a hit

        Units are ADC counts"""
        self.threshold = threshold

    def getThreshold(self):
        return self.threshold

    def ProcessHits(self, key, hits):
        """ process hits within a single bar"""
        counts_adc = 0
        counts_tdc = 0
        index_layer = key[0]
        index_bar   = key[1]
        for hit in hits:
            assert hit['layer'] == index_layer
            assert hit['bar'] == index_bar
            counts_adc += hit['dedx'] * self.energy_scale


        if counts_adc > self.getThreshold() or True:
            digit = {}
            digit['type'] = 'digit'
            digit['layer'] = index_layer
            digit['bar'] = index_bar
            digit['number_run'] = hit['number_run']
            digit['number_event'] = hit['number_event']
            digit['view'] = hit['view']
            digit['counts_adc'] = counts_adc
            digit['position'] = hit['position_bar']  # this should be derived
            
            self.digits.append(digit)

    def Commit(self):
        self.log.info('Bulk commit of digits in progress')
        self.log.debug('Size of digit bulk commit in bytes: %d', sys.getsizeof(self.digits))
        for doc in self.db.update(self.digits):
            self.log.debug('\tsaved: %s' % repr(doc))
        
        self.digits = []
