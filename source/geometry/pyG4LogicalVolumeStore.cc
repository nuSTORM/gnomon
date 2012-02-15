//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
// $Id: pyG4LogicalVolume.cc,v 1.5 2008-03-13 07:32:18 kmura Exp $
// $Name: not supported by cvs2svn $
// ====================================================================
//   pyG4LogicalVolume.cc
//
//                                         2005 Q
// ====================================================================
#include <boost/python.hpp>
#include "G4Version.hh"
#include "G4LogicalVolume.hh"
#include "G4Material.hh"
#include "G4VSolid.hh"
#include "G4FieldManager.hh"
#include "G4VSensitiveDetector.hh"
#include "G4UserLimits.hh"
#include "G4SmartVoxelHeader.hh"
#include "G4GeometryManager.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4MaterialCutsCouple.hh"
#include "G4FastSimulationManager.hh"

#include "pyG4indexing.hh"

using namespace boost::python;


namespace pyG4LogicalVolumeStore {

G4LogicalVolume* fetchVolumeNumber(G4LogicalVolumeStore* my_instance, int i) {
  return my_instance->at(i);
}
};

void export_G4LogicalVolumeStore()
{
  class_<G4LogicalVolumeStore, G4LogicalVolumeStore*, boost::noncopyable>
    ("G4LogicalVolumeStore", "logical volume store class", no_init)
      .def("GetInstance",           &G4LogicalVolumeStore::GetInstance,
           return_value_policy<reference_existing_object>())
      .staticmethod("GetInstance")
      .def("GetVolumeID",     &pyG4LogicalVolumeStore::fetchVolumeNumber,     return_internal_reference<>())
      .def("GetVolume",     &G4LogicalVolumeStore::GetVolume,     return_internal_reference<>())
      ;
}
//}
