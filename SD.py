import math
import Geant4 as G4

class ScintSD(G4.G4VSensitiveDetector):
    "SD for scint"

    def __init__(self):
        G4.G4VSensitiveDetector.__init__(self, "Scintillator")
        self.pos = {}
        self.pos['X'] = []
        self.pos['Y'] = []

    def getView(self, lv):
        view = None
        if str(lv.GetName())[-1] == 'X':
            view = 'X'
        elif str(lv.GetName())[-1] == 'Y':
            view = 'Y'

        return view
    def getMCHitPos(self, position, translation, view, width=10, thickness=5):
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

        if math.fabs(diff) > float(width)/2:
            raise ValueError

        return diff
    
    def ProcessHits(self, step, rohist):
        preStepPoint = step.GetPreStepPoint()
        if(preStepPoint.GetCharge() == 0):
            return

        track = step.GetTrack()

        pv = preStepPoint.GetPhysicalVolume()
        dedx = step.GetTotalEnergyDeposit()
        lv = pv.GetMotherLogical()

        print '\tcopy:',pv.GetCopyNo()
        print '\ttranslation:', pv.GetTranslation()
        print '\tposition:', preStepPoint.GetPosition()
        print '\tdedx:', dedx

        position = step.GetPostStepPoint().GetPosition()
        translation = pv.GetTranslation()
        view = self.getView(lv)

        print self.getMCHitPos(position, translation, view)

        print "*********" , (pv.GetTranslation() - preStepPoint.GetPosition())

        #if str(lv.GetName())[-1] == 'Y':
        #    f.write('Y %d %f\n' % (pv.GetCopyNo(), preStepPoint.GetPosition().y - pv.GetTranslation().y))
        #else:
        #    f.write('X %d %f\n' % (pv.GetCopyNo(), preStepPoint.GetPosition().x - pv.GetTranslation().x))

        #print '\trotation:', pv.GetRotation()                                                                                  
        #print '\tobjectRotationValue:', pv.GetObjectRotationValue()                                                            
        #print '\tframeRotation:', pv.GetFrameRotation()   
