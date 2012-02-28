"""The Digitization routines are for simulating electronics response in various
ways.  Oh, and we use USA spelling here, so use a 'zed' and like it."""

import Geant4 as G4
import Configuration

class VlenfSimpleDigitizer():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""
    
    def __init__(self):
        self.config = Configuration.DEFAULT()

        self.keep_mc_hits = False
        self.energy_scale = 20 # pe / MeV
        
        self.map_fun = """
function(doc) {
  if (doc.type == 'mchit')
    emit(doc.type, doc);
 }"""

        self.db = self.config.getCurrentDB()

    def FetchThenProcess(self, run, event):
        hits_dict = {}

        for row in self.db.query(self.map_fun):
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
        
        self.db.save(digit)
        #print 'counts', counts_adc

