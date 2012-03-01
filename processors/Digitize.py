"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""

import Geant4 as G4
import Configuration

class VlenfSimpleDigitizer():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.DEFAULT()

        self.keep_mc_hits = False
        self.energy_scale = 20.0 # pe / MeV
        elf.debug('Energy scale: %f', self.energy_scale)

        self.db = self.config.getCurrentDB()

        self.digits = []


    def FetchThenProcess(self, run, event):
        hits_dict = {}

        map_fun = """
function(doc) {
  if (doc.number_run == %d && doc.number_event == %d && doc.type == 'mchit')
    emit(doc.type, doc);
 }""" % (self.config.getRunNumber(), self.config.getEventNumber())

        for row in self.db.query(map_fun):
            doc = row.value

            i = doc['layer']
            j = doc['bar']

            if (i,j) not in hits_dict:
                hits_dict[(i,j)] = []

            hits_dict[(i,j)].append(dict(doc))

            if not self.keep_mc_hits:
                self.db.delete(doc)

        for key in hits_dict:
            self.Process(key, hits_dict[key])

        self.Commit()

    def Process(self, key, hits):
        counts_adc = 0
        counts_tdc = 0
        index_layer = key[0]
        index_bar   = key[1]
        for hit in hits:
            assert hit['layer'] == index_layer
            assert hit['bar'] == index_bar
            counts_adc += hit['dedx'] * self.energy_scale

        digit = {}
        digit['type'] = 'digit'
        digit['layer'] = index_layer
        digit['bar'] = index_bar
        digit['number_run'] = hit['number_run']
        digit['number_event'] = hit['number_event']
        digit['view'] = hit['view']
        digit['counts_adc'] = counts_adc

        self.digits.append(digit)

    def Commit(self):
        self.db.update(self.digits)
        self.digits = []
