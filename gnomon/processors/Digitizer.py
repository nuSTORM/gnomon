"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""


from gnomon.processors import Base


class VlenfSimpleDigitizer(Base.Processor):
    """The VLENF digitizer where the energy deposited is multiplied by a
    generic energy scale."""

    def __init__(self):
        """Initialize with defaults digitization files
        """
        Base.Processor.__init__(self)

        self.energy_scale = 80.0  # pe / MeV
        self.log.debug('Energy scale: %f', self.energy_scale)

        self.threshold = None  # [ADC counts], to be set on next line
        self.set_threshold()

    def process(self, docs):
        new_docs = []  # Modified documents
        hits_dict = {}  # Used to combine hits in same bar

        for doc in docs:
            #  For every document, see if it's an MC hit
            if doc['type'] != 'mchit':
                new_docs.append(doc)
                continue

            # If MC hit, then extract where the hit was
            layer = doc['layer']
            view = doc['view']
            position_bar = doc['position_bar']

            # Form unique location key
            key = (doc['run'], doc['event'], layer, doc['bar'], view)

            #  If first hit here, create array to store these hits
            if key not in hits_dict.keys():
                hits_dict[key] = []

            #  Determine what is 'seen'
            counts_adc = doc['dedx'] * self.energy_scale

            #  Create digit
            digit = {}
            digit['type'] = 'digit'
            digit['run'] = doc['run']
            digit['event'] = doc['event']
            digit['layer'] = layer
            digit['bar'] = doc['bar']
            digit['view'] = view
            digit['counts_adc'] = counts_adc
            digit['position'] = position_bar  # this should be derived

            #  Append digit to list of hits for this bar
            hits_dict[key].append(digit)

        # Combine hits from same bar
        partial_digit = None
        for key, value in hits_dict.iteritems():
            # Sum hits in bar
            total_counts_adc = 0
            for partial_digit in value:
                total_counts_adc += partial_digit['counts_adc']

            total_counts_adc = int(total_counts_adc)

            #  Only save if passes threshold
            if total_counts_adc > self.get_threshold():
                if partial_digit is not None:
                    partial_digit['counts_adc'] = total_counts_adc
                    new_docs.append(partial_digit)

        return new_docs

    def set_threshold(self, threshold=2):
        """Threshold for registering a hit

        Units are adc counts"""
        self.threshold = threshold

    def get_threshold(self):
        return self.threshold
