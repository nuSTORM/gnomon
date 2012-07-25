"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""

import logging
import sys

class VlenfSimpleDigitizer():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.energy_scale = 80.0 # pe / MeV
        self.log.debug('Energy scale: %f', self.energy_scale)

        self.threshold = None
        self.setThreshold()

    def Shutdown(self):
        pass

    def Process(self, docs):
        new_docs = []
        hits_dict = {}

        for doc in docs:
            if doc['type'] != 'mchit':
                new_docs.append(doc)
                continue

            run = doc['run']
            event = doc['event']
            layer = doc['layer']
            bar = doc['bar']
            view = doc['view']
            position_bar = doc['position_bar']

            key = (run, event, layer, bar, view)

            if key not in hits_dict.keys():
                hits_dict[key] = []

            dedx = doc['dedx']
            counts_adc = dedx * self.energy_scale

            digit = {}
            digit['type'] = 'digit'
            digit['run'] = run
            digit['event'] = event
            digit['layer'] = layer
            digit['bar'] = bar
            digit['view'] = view
            digit['counts_adc'] = counts_adc
            digit['position'] = position_bar  # this should be derived

            hits_dict[key].append(digit)


        for key, value in hits_dict.iteritems():
            total_counts_adc = 0
            for partial_digit in value:
                total_counts_adc += partial_digit['counts_adc']

            total_counts_adc = int(total_counts_adc)

            if total_counts_adc > self.getThreshold():
                partial_digit['counts_adc'] = total_counts_adc
                new_docs.append(partial_digit)

        return new_docs

    def setThreshold(self, threshold = 2):
        """Threshold for registering a hit

        Units are ADC counts"""
        self.threshold = threshold

    def getThreshold(self):
        return self.threshold
