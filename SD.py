import math
import couchdb
import Geant4 as G4


class ScintSD(G4.G4VSensitiveDetector):
    "SD for scint bar"

    def __init__(self, layers, bars, width, thickness):
        G4.G4VSensitiveDetector.__init__(self, "Scintillator")

        self.layers = layers
        self.bars = bars
        self.width = width
        self.thickness = thickness

        self.pos = {}
        self.pos['X'] = []
        self.pos['Y'] = []

        self.couch = couchdb.Server()

        db_name = 'mc_hit'
        if db_name in self.couch:
            self.couch.delete(db_name)
        self.db = self.couch.create(db_name)

    def getView(self, lv):
        view = None
        if str(lv.GetName())[-1] == 'X':
            view = 'X'
        elif str(lv.GetName())[-1] == 'Y':
            view = 'Y'

        return view

    # These should come from G4GDMLParser!! thickness, width
    def getMCHitPos(self, position, trans, long, translation, view, width=10, thickness=5):
        diff = None
        if view == 'X':
            diff = position.x - translation.x
        elif view == 'Y':
            diff = position.y - translation.y
        else:
            raise TypeError

        self.pos[view].append(diff)

        if len(self.pos['X']) and len(self.pos['Y']):
            print 'X: [%f, %f], Y: [%f, %f]' % (min(self.pos['X']), max(self.pos['X']), min(self.pos['Y']), max(self.pos['Y']))


        if math.fabs(diff) > float(width) / 2:
            raise ValueError

        return translation

    def ProcessHits(self, step, rohist):
        preStepPoint = step.GetPreStepPoint()
        if(preStepPoint.GetCharge() == 0):
            return

        theTouchable = preStepPoint.GetTouchable()
        copyNo = theTouchable.GetCopyNumber(0)
        motherCopyNo = theTouchable.GetCopyNumber(1)
        depth = theTouchable.GetHistoryDepth()
        print 'depth', depth

        for i in range(depth+1):
            print '\t', i, theTouchable.GetCopyNumber(i), theTouchable.GetReplicaNumber(i)

        trans = theTouchable.GetCopyNumber(0)
        long = theTouchable.GetCopyNumber(2)

        track = step.GetTrack()

        pv = preStepPoint.GetPhysicalVolume()
        dedx = step.GetTotalEnergyDeposit()
        lv = pv.GetMotherLogical()

        print '\tcopy:', pv.GetCopyNo()
        print '\ttranslation:', pv.GetTranslation()
        print '\tposition:', preStepPoint.GetPosition()
        print '\tdedx:', dedx

        position = step.GetPostStepPoint().GetPosition()
        translation = pv.GetTranslation()
        view = self.getView(lv)

        print self.getMCHitPos(position, translation, view)

        doc = {}
        doc['type'] = 'mchit'
        doc['dedx'] = dedx
        doc['position'] = {'x' : position.x,
                           'y' : position.y,
                           'z' : position.z}

        doc['copy0'] = theTouchable.GetCopyNumber(0)
        doc['copy2'] = theTouchable.GetCopyNumber(2)
        doc['view'] = view
        
        self.db.save(doc)

