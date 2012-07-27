"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""

import logging


class VlenfSimpleDigitizer():
    """The VLENF digitizer where the energy deposited is multiplied by a
    generic energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.energy_scale = 80.0  # pe / MeV
        self.log.debug('Energy scale: %f', self.energy_scale)

        self.threshold = None
        self.set_threshold()

    def shutdown(self):
        pass

    def process(self, docs):
        new_docs = []
        hits_dict = {}

        for doc in docs:
            if doc['type'] != 'mchit':
                new_docs.append(doc)
                continue

            layer = doc['layer']
            view = doc['view']
            position_bar = doc['position_bar']

            key = (doc['run'], doc['event'], layer, doc['bar'], view)

            if key not in hits_dict.keys():
                hits_dict[key] = []

            counts_adc = doc['dedx'] * self.energy_scale

            digit = {}
            digit['type'] = 'digit'
            digit['run'] = doc['run']
            digit['event'] = doc['event']
            digit['layer'] = layer
            digit['bar'] = doc['bar']
            digit['view'] = view
            digit['counts_adc'] = counts_adc
            digit['position'] = position_bar  # this should be derived

            hits_dict[key].append(digit)

        partial_digit = None
        for key, value in hits_dict.iteritems():
            total_counts_adc = 0
            for partial_digit in value:
                total_counts_adc += partial_digit['counts_adc']

            total_counts_adc = int(total_counts_adc)

            if total_counts_adc > self.get_threshold():
                if partial_digit is not None:
                    partial_digit['counts_adc'] = total_counts_adc
                    new_docs.append(partial_digit)

        return new_docs

    def set_threshold(self, threshold=2):
        """Threshold for registering a hit

        Units are ADC counts"""
        self.threshold = threshold

    def get_threshold(self):
        return self.threshold
