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


    def ProcessEvent(self, run, event):
        hits_dict = {}

        map_fun = """
function(doc) {
if (doc.number_run == %d && doc.number_run == %d && doc.type == 'mchit')
emit([doc.layer, doc.bar, doc.view], doc.dedx);
 }""" % (run, event)

        """TODO All this logic below could be made a reduce instead"""

        for row in self.db.query(map_fun, include_docs=True):
            doc = row.doc

            if row.key not in hits_dict:
                hits_dict[row.key] = []

            hits_dict[row.key].append(dict(doc))

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
        index_layer, index_bar, index_view = key
        for hit in hits:
            assert hit['layer'] == index_layer
            assert hit['bar']   == index_bar
            assert hit['view']  == index_view
            counts_adc += hit['dedx'] * self.energy_scale

        if counts_adc > self.getThreshold() or True:
            digit = {}
            digit['type'] = 'digit'
            digit['layer'] = index_layer
            digit['bar'] = index_bar
            digit['number_run'] = hit['number_run']
            digit['number_event'] = hit['number_event']
            digit['view'] = index_view
            digit['counts_adc'] = counts_adc
            digit['position'] = hit['position_bar']  # this should be derived
            
            self.digits.append(digit)

    def Commit(self):
        self.log.info('Bulk commit of digits in progress')
        self.log.debug('Size of digit bulk commit in bytes: %d', sys.getsizeof(self.digits))
        for doc in self.db.update(self.digits):
            self.log.debug('\tsaved: %s' % repr(doc))
        
        self.digits = []
