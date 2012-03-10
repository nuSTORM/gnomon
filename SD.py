import math
import logging
import sys

import random  #  used for random,
import time    #  wait if connection dies

import Geant4 as G4
import Configuration

class ScintSD(G4.G4VSensitiveDetector):
    "SD for scint bar"

    def __init__(self, layers, bars, width, thickness_layer, thickness_bar):
        G4.G4VSensitiveDetector.__init__(self, "Scintillator")

        random.seed()

        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        # todo: just pass gdml object
        self.layers = layers
        self.bars = bars
        self.width = width
        self.thickness_layer = thickness_layer
        self.thickness_bar = thickness_bar

        self.log.debug('layers: %f', layers)
        self.log.debug('bars: %f', bars)
        self.log.debug('width: %f', width)
        self.log.debug('thickness_layer: %f', thickness_layer)
        self.log.debug('thickness_bar: %f', thickness_bar)

        self.config = Configuration.DEFAULT()
        self.commit_threshold = self.config.getCommitThreshold()
        self.db = self.config.getCurrentDB()
        
        self.event = 0
        
        self.use_bulk_commits = True
        self.mc_hits = []

    def setEventNumber(self, number):
        if isinstance(number, int):
            self.event = number
        else:
            raise TypeError('Not an int event number')

    def getNumberOfBars(self):
        """Return the number of bars per view"""
        return self.bars

    def getNumberOfLayers(self):
        """Return the number of layers in z, where a layer is steel plus
        two views"""
        return self.layers

    def getView(self, lv):
        """Determine the detector view starting with a G4LogicalVolume"""
        view = None
        if str(lv.GetName())[-1] == 'X':
            return 'X'
        elif str(lv.GetName())[-1] == 'Y':
            return 'Y'
        
        self.log.error('Cannot determine view for %s', lv.GetName())
        raise 'Cannot determine view for %s' % lv.GetName()
        return view

    def getMCHitBarPosition(self, layer_number, bar_number, view, position):
        doc = {}

        guess_z = self.thickness_layer * layer_number

        #  TODO This requires more investigation.  See issue #4
        #  Ordering in increasing beam-axis, ie z-axis: steel, X, Y
        if view == 'X':
            guess_z += self.thickness_layer - 2 * self.thickness_bar
        else:
            guess_z += self.thickness_layer - 1 * self.thickness_bar

        guess_z += self.thickness_bar / 2 # Go to middle of bar

        guess_z -= self.thickness_layer * self.layers/2 # Set 0 to middle

        doc['z'] = guess_z

        # 0.1 mm tolerance
        self.log.debug('Finding bar longitudinal position')
        self.log.debug('\tGuess in z: %f', guess_z)
        self.log.debug('\tPosition in z: %f', position.z)
        diff = math.fabs(guess_z - position.z)
        threshold = self.thickness_bar/2 + 0.1 * G4.mm 
        assert diff <= threshold

        guess_trans = bar_number
        guess_trans = self.width * (guess_trans - self.bars/2) + self.width/2
        if view == 'X':
            trans = position.x
            doc['x'] = guess_trans
            doc['y'] = 0
        elif view == 'Y':
            trans = position.y
            doc['y'] = guess_trans
            doc['x'] = 0

        # 0.1 mm tolerance
        self.log.debug('Finding bar transverse position')
        self.log.debug('\tGuess in z: %f', guess_trans)
        self.log.debug('\tPosition in z: %f', trans)
        diff = math.fabs(trans-guess_trans)
        threshold = self.width/2 + 1 * G4.mm
        assert diff <= threshold

        return doc

    def ProcessHits(self, step, rohist):
        preStepPoint = step.GetPreStepPoint()

        if step.GetTotalEnergyDeposit() == 0.0:
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
        doc['number_event'] = self.event #self.config.getEventNumber()

        doc['position_bar']  = self.getMCHitBarPosition(doc['layer'],
                                                        doc['bar'],
                                                        doc['view'],
                                                        position)

        self.log.info("View %s" % view)

        self.mc_hits.append(doc)
        self.bulkCommit()


    def getUseBulkCommits(self):
        """Should SD perform bulk commits to CouchDB"""
        return self.use_bulk_commits
            
    def bulkCommit(self, force=False):
        """Perform bulk commit of mchits

        Commit to couchdb all mchits for the event and then clear cache"""
        self.log.info('Bulk commit of mchits requested')
        size = sys.getsizeof(self.mc_hits)
        self.log.debug('Size of digit bulk commit in bytes: %d' % size)
        if size > self.commit_threshold or force:
            self.log.info('Commiting %d bytes to CouchDB' % size)
            try:
                self.db.update(self.mc_hits)
            except:
                log.error('Failed to upload mchits to CouchDB, retrying...')
                wait_time = random.randint(60,120) # wait between 60 s and 120 s
                time.sleep(wait_time)
                self.db.update(self.mc_hits)
            self.mc_hits = []
