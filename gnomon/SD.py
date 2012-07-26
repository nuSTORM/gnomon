import math
import logging
import random

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

        self.config = Configuration.GLOBAL_CONFIG
        self.docs = []
        self.event = 0

    def getDocs(self):
        return self.docs

    def clearDocs(self):
        self.docs = []

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

    def getMCHitBarPosition(self, layer_number, bar_number, view, position, guess_z):
        doc = {}

        doc['z'] = guess_z

        diff = math.fabs(guess_z - position.z)
        threshold = self.thickness_bar / 2 + 0.1 * G4.mm   # 0.1 mm tolerance

        try:
            assert diff <= threshold
        except:
            self.log.error('Bad longitudinal position: Guess in z: %f, Position in z: %f, View: %s', guess_z, position.z, view)
            raise

        guess_trans = bar_number
        guess_trans = self.width * (guess_trans - self.bars / 2) + \
            self.width / 2
        if view == 'X':
            trans = position.x
            doc['x'] = guess_trans
            doc['y'] = 0
        elif view == 'Y':
            trans = position.y
            doc['y'] = guess_trans
            doc['x'] = 0

        diff = math.fabs(trans - guess_trans)
        threshold = self.width / 2 + 1 * G4.mm  # 0.1 mm tolerance

        try:
            assert diff <= threshold
        except:
            self.log.error('Bad transverse position: Guess in z: %f, Position in z: %f',
                           guess_trans, trans)
            raise

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

        doc['run'] = self.config['run_number']
        doc['event'] = self.event

        doc['position_bar'] = self.getMCHitBarPosition(doc['layer'],
                                                       doc['bar'],
                                                       doc['view'],
                                                       position,
                                                       theTouchable.GetTranslation(0).z)

        self.docs.append(doc)
