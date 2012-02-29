import math
import couchdb
import Geant4 as G4
import Configuration

class ScintSD(G4.G4VSensitiveDetector):
    "SD for scint bar"

    def __init__(self, layers, bars, width, thickness_layer, thickness_bar):
        G4.G4VSensitiveDetector.__init__(self, "Scintillator")

        # todo: just pass gdml object
        self.layers = layers
        self.bars = bars
        self.width = width
        self.thickness_layer = thickness_layer
        self.thickness_bar = thickness_bar

        self.config = Configuration.DEFAULT()
        
        self.use_bulk_commits = True
        self.mc_hits = []

    def getNumberOfBars(self):
        """Return the number of bars per view"""
        return self.bars

    def getNumberOfLayers(self):
        """Return the number of layers in z, where a layer is steel plus
        two views"""
        return self.layers

    def getView(self, lv):
        view = None
        if str(lv.GetName())[-1] == 'X':
            view = 'X'
        elif str(lv.GetName())[-1] == 'Y':
            view = 'Y'

        return view

    def getMCHitBarPosition(self, layer_number, bar_number, view, position):
        doc = {}

        guess_z = self.thickness_layer * (layer_number - self.layers/2)

        if view == 'X':
            guess_z += self.thickness_bar/2
        else:
            guess_z += 3 * self.thickness_bar/2
        guess_z += (self.thickness_layer - 2 * self.thickness_bar)

        doc['z'] = guess_z

        # 0.1 mm tolerance
        diff = math.fabs(guess_z - position.z)
        assert diff <= self.thickness_bar/2 + 0.1 * G4.mm

        guess_trans = bar_number
        guess_trans = self.width * (guess_trans - self.bars/2) + self.width/2
        if view == 'X':
            trans = position.x
            doc['x'] = guess_trans
        elif view == 'Y':
            trans = position.y
            doc['y'] = guess_trans

        # 0.1 mm tolerance
        diff = math.fabs(trans-guess_trans)
        assert diff <= self.width/2 + 1 * G4.mm

        return doc

    def ProcessHits(self, step, rohist):
        preStepPoint = step.GetPreStepPoint()
        if(preStepPoint.GetCharge() == 0):
            return

        theTouchable = preStepPoint.GetTouchable()
        copyNo = theTouchable.GetCopyNumber(0)
        motherCopyNo = theTouchable.GetCopyNumber(1)

        pv = preStepPoint.GetPhysicalVolume()
        dedx = step.GetTotalEnergyDeposit()
        lv = pv.GetMotherLogical()

        position = step.GetPostStepPoint().GetPosition()
        view = self.getView(lv)

        doc = {}
        doc['type'] = 'mchit'
        doc['dedx'] = dedx
        doc['position'] = {'x': position.x,
                           'y': position.y,
                           'z': position.z}

        doc['bar'] = theTouchable.GetCopyNumber(0)
        doc['layer'] = theTouchable.GetCopyNumber(2)
        doc['view'] = view

        doc['number_run'] = self.config.getRunNumber()
        doc['number_event'] = self.config.getEventNumber()

        doc['position_bar'] = self.getMCHitBarPosition(doc['layer'],
                                                       doc['bar'],
                                                       doc['view'],
                                                       position)


        if self.use_bulk_commits:
            self.mc_hits.append(doc)
        else:
            self.config.getCurrentDB().save(doc)

    def getUseBulkCommits(self):
        return self.use_bulk_commits
            
    def bulkCommit(self):
        self.config.getCurrentDB().update(self.mc_hits)
        self.mc_hits = []
