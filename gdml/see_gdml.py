from math import *
 
import ROOT
import writer
import ROOTwriter
 
# get TGeoManager and
# get the top volume of the existing (in-memory) geometry tree
geomgr = ROOT.gGeoManager
topV = geomgr.GetTopVolume()
 
# instanciate writer
gdmlwriter = writer.writer('mygeo.gdml')
binding = ROOTwriter.ROOTwriter(gdmlwriter)
 
# dump materials
matlist = geomgr.GetListOfMaterials()
binding.dumpMaterials(matlist)
 
# dump solids
shapelist = geomgr.GetListOfShapes()
binding.dumpSolids(shapelist)
 
# dump geo tree
print 'Traversing geometry tree'
gdmlwriter.addSetup('default', '1.0', topV.GetName())
binding.examineVol(topV)
 
# write file
gdmlwriter.writeFile()
